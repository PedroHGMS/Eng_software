# reviews/views.py

from django.db.models import Avg, Count, Q

from universities.models import Professor, Universidade, Disciplina
from .forms import ReviewForm
from .models import Review

from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model # Importa get_user_model
from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.template.loader import render_to_string
from django.http import JsonResponse, HttpResponse # Importa HttpResponse para debug se necessário
from django.urls import reverse # Importar para gerar URLs (redirecionamento via JS)
from django.views.decorators.http import require_POST # Opcional: para restringir a POST
# from django.views.decorators.csrf import csrf_protect # @csrf_protect é implícito com @require_POST e Django form

from math import floor

# Obtém o modelo de usuário ativo (auth.User ou modelo customizado)
User = get_user_model()

@login_required
def all_reviews(request):
    professors = Professor.objects.annotate(
        avg_rate=Avg("review__qualidade"),
        total_reviews=Count("review", distinct=True),
        total_subjects=Count("review__disciplina", distinct=True)
    ).filter(total_reviews__gt=0).order_by("?")

    top_disciplinas = Disciplina.objects.annotate(
        avg_quality=Avg("review__qualidade"),
        total_reviews=Count("review")
    ).filter(total_reviews__gt=0).order_by("-avg_quality")[:5]

    top_universidades = Universidade.objects.annotate(
        avg_quality=Avg("professor__review__qualidade"),
        total_reviews=Count("professor__review")
    ).filter(total_reviews__gt=0).order_by("-avg_quality")[:5]

    return render(request, "reviews/reviews.html", {
        "professors": professors,
        "top_disciplinas": top_disciplinas,
        "top_universidades": top_universidades,
    })


@login_required
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
    ordenar = request.GET.get('ordenar', 'newest')  # Default order

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
    for review in filtered_ordered_reviews_queryset:  # Itera sobre o queryset filtrado/ordenado
        review.filled_quality_stars = review.qualidade
        review.empty_quality_stars = 5 - review.qualidade
        review.filled_difficulty_circles = review.dificuldade
        review.empty_difficulty_circles = 5 - review.dificuldade
        processed_reviews.append(review)

    # --- 6. Paginação (do queryset FILTRADO/ORDENADO) ---
    paginator = Paginator(processed_reviews, 10)  # Pagina a lista processada
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # --- Context Dictionary ---
    # O contexto inclui tanto dados totais (estatísticas) quanto dados filtrados (lista de reviews)
    context = {
        'professor': professor,
        'reviews': page_obj,  # Passa a lista paginada de reviews processados (FILTRADA/ORDENADA)
        'is_paginated': page_obj.has_other_pages(),
        'page_obj': page_obj,
        'averages': averages,  # Estatísticas totais
        'avg_quality_icons': avg_quality_icons,  # Estatísticas totais
        'avg_difficulty_icons': avg_difficulty_icons,  # Estatísticas totais
        'quality_distribution': full_quality_distribution,  # Estatísticas totais
        'difficulty_distribution': full_difficulty_distribution,  # Estatísticas totais
        'total_reviews': total_reviews,  # Estatísticas totais
        # Passa back current filter/sort values to retain selection in template
        'current_order': ordenar,
        'current_disciplina': filter_disciplina,
        'current_periodo': filter_periodo,
        'disciplinas': disciplinas,  # Disciplinas disponíveis para filtro (TOTAIS)
        'periodos': periodos,  # Períodos disponíveis para filtro (TOTAIS)
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

@login_required
def search_reviews(request):
    query = request.GET.get('q', '').strip()
    professors_found = Professor.objects.none() # Default empty queryset

    if query:
        # Construir um filtro Q para buscar em múltiplos campos
        # Use icontains para case-insensitive contains
        # Use distinct() para garantir professores únicos
        professor_filter = Q(professor__name__icontains=query)
        disciplina_filter = Q(disciplina__nome__icontains=query)
        descricao_filter = Q(descricao__icontains=query)
        periodo_filter = Q(periodo__icontains=query) # Incluir busca por período

        # Combine os filtros com OR (|)
        matching_reviews = Review.objects.filter(
           professor_filter | disciplina_filter | descricao_filter | periodo_filter
        ).select_related('professor').distinct() # Use select_related para eficiência ao acessar professor

        # Obter os IDs dos professores distintos encontrados nas reviews
        professor_ids = matching_reviews.values_list('professor__id', flat=True)

        # Se houver IDs, busque os objetos Professor
        if professor_ids.exists(): # Use exists() para verificar se a lista não está vazia
            # Filtra os professores pelos IDs encontrados e anota as estatísticas relevantes
            professors_found = Professor.objects.filter(id__in=professor_ids).annotate(
                 avg_rate=Avg("review__qualidade"),
                 total_reviews=Count("review", distinct=True),
                 total_subjects=Count("review__disciplina", distinct=True)
             ).order_by('name') # Ordena por nome

    # Incluir o contexto para a busca
    context = {
        'query': query,
        'professors_found': professors_found # Passa o queryset de professores encontrados
    }

    # Renderiza o template de resultados da busca
    return render(request, 'reviews/search_results.html', context)

@login_required # Garante que apenas usuários logados possam acessar
# @require_POST # Opcional: Descomente esta linha se quiser que esta URL só aceite requisições POST
def MakeReview(request):
    """
    View para criar uma nova review.
    Lida com submissões GET (exibir formulário) e POST (processar formulário via AJAX ou tradicional).
    """

    if request.method == 'POST':
        form = ReviewForm(request.POST)
        form.instance.usuario = request.user # Atribui o usuário logado

        if form.is_valid():
            review = form.save()

            # --- RESPOSTA PARA REQUISIÇÃO AJAX (handled by make_review.js) ---
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                # Sucesso: Retorna JsonResponse indicando sucesso e uma URL de redirecionamento
                try:
                    # --- ALTERAÇÃO AQUI ---
                    # Defina a URL de redirecionamento desejada. Ex: página de todos os reviews
                    new_redirect_url = reverse('reviews:success')

                    return JsonResponse({'success': True, 'message': 'Review enviado com sucesso!', 'redirect_url': new_redirect_url})

                except Exception as e:
                    # Se algo der errado ao gerar a NOVA URL de redirecionamento, ainda retorne sucesso
                    print(f"Erro ao gerar a nova URL de redirecionamento após salvar review {review.id}: {e}") # Logar erro no servidor
                    # Como fallback, você pode retornar uma URL padrão ou nenhuma URL
                    # Ex: Redirecionar para a lista de professores ou homepage
                    fallback_url = reverse('reviews:success') # Fallback, pode ser outra URL padrão se preferir
                    return JsonResponse({'success': True, 'message': 'Review enviado com sucesso, mas houve um problema ao redirecionar.', 'redirect_url': fallback_url})


            # --- RESPOSTA PARA SUBMISSÃO TRADICIONAL (fallback, se JS estiver desabilitado) ---
            else:
                # Redireciona o navegador
                # --- ALTERAÇÃO AQUI ---
                # Redirecione para a URL desejada. Ex: página de todos os reviews
                return redirect('reviews:all_reviews') # <--- Mude 'reviews:all_reviews' para o nome da URL desejada


        else: # Formulário inválido
            # Handle requisição AJAX com formulário inválido
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'errors': form.errors}, status=400)

            # Handle submissão tradicional com formulário inválido
            else:
                pass # Continua para renderizar o template com erros


    # O código só chega aqui se a requisição for GET, ou POST inválido tradicional
    # --- CONTEXTO PARA RENDERIZAÇÃO DO TEMPLATE (usado por GET e POST inválido tradicional) ---
    if request.method == 'GET':
         form = ReviewForm()

    context = {
        'form': form,
    }

    return render(request, 'reviews/make_review.html', context)

# A view de sucesso pode ser simples, talvez apenas renderizar uma mensagem.
# No fluxo AJAX/JS, o redirecionamento ou reset do formulário é feito pelo JS,
# então esta view pode não ser estritamente necessária se você sempre usar AJAX.
# No entanto, é útil como fallback ou para confirmação visual simples.
@login_required
def MakeReviewSucess(request):
    # Pode passar alguma mensagem ou contexto se necessário
    # context = {'message': 'Sua avaliação foi enviada com sucesso!'}
    return render(request, 'reviews/make_review_success.html') # Certifique-se que este template existe