from django.shortcuts import render
from django.db.models import Avg, Count
from .models import Review
from universities.models import Professor
from django.db.models import Q
from django.contrib.auth import logout
from django.shortcuts import redirect


def all_reviews(request):
    professors = Professor.objects.annotate(
        avg_rate=Avg("review__qualidade"),
        total_reviews=Count("review", distinct=True),
        total_subjects=Count("review__disciplina", distinct=True)
    ).filter(total_reviews__gt=0)

    return render(request, "reviews/reviews.html", {"professors": professors})



from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.db.models import Avg, Count
from django.db.models import Q
from django.template.loader import render_to_string
from django.http import JsonResponse, HttpResponse # Import HttpResponse
from .models import Review
from universities.models import Professor, Disciplina
from math import floor, ceil # Para calcular estrelas/círculos para médias

def professor_reviews_view(request, professor_id):
    professor = get_object_or_404(Professor, id=professor_id)

    # --- 1. Queryset Total (para estatísticas) ---
    # Este queryset NUNCA é filtrado pela requisição GET
    initial_reviews_queryset = Review.objects.filter(professor=professor)

    # --- 2. Queryset Filtrado/Ordenado (para a lista de reviews) ---
    # Começa com o queryset total e aplica filtros/ordenação
    filtered_ordered_reviews_queryset = initial_reviews_queryset

    # Get filter and sort parameters from GET request
    filter_disciplina = request.GET.get('disciplina', '')
    filter_periodo = request.GET.get('periodo', '')
    ordenar = request.GET.get('ordenar', 'newest') # Default order

    # Apply filtering
    if filter_disciplina:
        filtered_ordered_reviews_queryset = filtered_ordered_reviews_queryset.filter(disciplina__id=filter_disciplina)
    if filter_periodo:
        filtered_ordered_reviews_queryset = filtered_ordered_reviews_queryset.filter(periodo=filter_periodo)

    # Define ordering based on the parameter
    sort_mapping = {
        'newest': '-periodo',
        'quality_desc': '-qualidade',
        'quality_asc': 'qualidade',
        'difficulty_desc': '-dificuldade',
        'difficulty_asc': 'dificuldade',
        'grade_desc': '-nota_obtida',
        'grade_asc': 'nota_obtida',
    }
    order_field = sort_mapping.get(ordenar, '-periodo')
    filtered_ordered_reviews_queryset = filtered_ordered_reviews_queryset.order_by(order_field)

    # --- 3. Get Unique Disciplines and Periods for Filters (do queryset Total) ---
    # As opções de filtro devem mostrar todas as opções disponíveis para este professor
    disciplinas = Disciplina.objects.filter(review__professor=professor).distinct().order_by('nome')
    periodos = initial_reviews_queryset.values_list('periodo', flat=True).distinct().order_by('-periodo')


    # --- 4. Calcular Estatísticas (Usando o queryset TOTAL) ---
    # Aggregate averages
    averages = initial_reviews_queryset.aggregate(
        Avg('dificuldade'),
        Avg('qualidade'),
        Avg('nota_obtida')
    )

    # Calculate raw counts per score
    quality_counts_qs = initial_reviews_queryset.values('qualidade').annotate(count=Count('qualidade')).order_by('-qualidade')
    difficulty_counts_qs = initial_reviews_queryset.values('dificuldade').annotate(count=Count('dificuldade')).order_by('-dificuldade')

    max_quality_count = max([item['count'] for item in quality_counts_qs] + [0])
    max_difficulty_count = max([item['count'] for item in difficulty_counts_qs] + [0])

    full_quality_distribution = []
    for score in range(5, 0, -1):
        count = next((item['count'] for item in quality_counts_qs if item['qualidade'] == score), 0)
        percentage = (count / max_quality_count * 100) if max_quality_count > 0 else 0
        full_quality_distribution.append({'score': score, 'count': count, 'percentage': percentage})

    full_difficulty_distribution = []
    for score in range(5, 0, -1):
        count = next((item['count'] for item in difficulty_counts_qs if item['dificuldade'] == score), 0)
        percentage = (count / max_difficulty_count * 100) if max_difficulty_count > 0 else 0
        full_difficulty_distribution.append({'score': score, 'count': count, 'percentage': percentage})

    # Calculate Visual Icons for Average Quality and Difficulty (Usando as médias totais)
    avg_quality = averages.get('qualidade__avg') or 0
    avg_difficulty = averages.get('dificuldade__avg') or 0

    def calculate_visual_icons_for_average(average):
        full_icons = floor(average)
        has_half = (average - full_icons) >= 0.5
        empty_icons = 5 - full_icons - (1 if has_half else 0)
        full_icons = max(0, full_icons)
        empty_icons = max(0, empty_icons)
        return {'full': full_icons, 'half': has_half, 'empty': empty_icons}

    avg_quality_icons = calculate_visual_icons_for_average(avg_quality)
    avg_difficulty_rounded = round(avg_difficulty)
    avg_difficulty_icons = {
        'full': max(0, min(5, avg_difficulty_rounded)),
        'half': False,
        'empty': max(0, 5 - max(0, min(5, avg_difficulty_rounded)))
    }

    # --- Total Reviews Count (do queryset TOTAL para as estatísticas) ---
    total_reviews = initial_reviews_queryset.count()

    # --- 5. Processar Reviews e Calcular Contagem de Ícones (do queryset FILTRADO/ORDENADO) ---
    processed_reviews = []
    for review in filtered_ordered_reviews_queryset: # Itera sobre o queryset filtrado/ordenado
        review.filled_quality_stars = review.qualidade
        review.empty_quality_stars = 5 - review.qualidade
        review.filled_difficulty_circles = review.dificuldade
        review.empty_difficulty_circles = 5 - review.dificuldade
        processed_reviews.append(review)

    # --- 6. Paginação (do queryset FILTRADO/ORDENADO) ---
    paginator = Paginator(processed_reviews, 10) # Pagina a lista processada
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # --- Context Dictionary ---
    # O contexto inclui tanto dados totais (estatísticas) quanto dados filtrados (lista de reviews)
    context = {
        'professor': professor,
        'reviews': page_obj, # Passa a lista paginada de reviews processados (FILTRADA/ORDENADA)
        'is_paginated': page_obj.has_other_pages(),
        'page_obj': page_obj,
        'averages': averages, # Estatísticas totais
        'avg_quality_icons': avg_quality_icons, # Estatísticas totais
        'avg_difficulty_icons': avg_difficulty_icons, # Estatísticas totais
        'quality_distribution': full_quality_distribution, # Estatísticas totais
        'difficulty_distribution': full_difficulty_distribution, # Estatísticas totais
        'total_reviews': total_reviews, # Estatísticas totais
        # Passa back current filter/sort values to retain selection in template
        'current_order': ordenar,
        'current_disciplina': filter_disciplina,
        'current_periodo': filter_periodo,
        'disciplinas': disciplinas, # Disciplinas disponíveis para filtro (TOTAIS)
        'periodos': periodos, # Períodos disponíveis para filtro (TOTAIS)
    }

    # --- AJAX Detection and Response ---
    is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest'

    if is_ajax:
        # Se for requisição AJAX, renderiza apenas a partial template
        # Passa o mesmo contexto para a partial
        html = render_to_string('reviews/includes/review_list.html', context, request=request)
        # Retorna a HTML dentro de um JSON para facilitar o processamento no JS
        return JsonResponse({'html': html})
        # Ou, se a parcial for o corpo inteiro da resposta, pode retornar HttpResponse(html)
        # return HttpResponse(html)

    else:
        # Se não for requisição AJAX, renderiza a template completa
        return render(request, 'reviews/single_professor_reviews.html', context)

def search_reviews(request):
    query = request.GET.get('q', '').strip()
    professors_found = Professor.objects.none()

    if query:
        matching_reviews = Review.objects.filter(
            Q(professor__name__icontains=query) |
            Q(disciplina__nome__icontains=query) |
            Q(descricao__icontains=query)
        ).distinct()

        professor_ids = matching_reviews.values_list('professor_id', flat=True).distinct()

        if professor_ids:
            professors_found = Professor.objects.filter(id__in=professor_ids).order_by('name')

    return render(request, 'reviews/search_results.html', {
        'query': query,
        'professors_found': professors_found
    })


def my_custom_logout_view(request):
    logout(request)
    return redirect('/')
