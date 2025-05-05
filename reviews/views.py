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

    # Cria uma instância do formulário.
    # Se a requisição for POST, popula com os dados recebidos; caso contrário, cria um formulário vazio.
    if request.method == 'POST':
        form = ReviewForm(request.POST)

        # --- PASSO CRUCIAL: ATRIBUIR O USUÁRIO AUTENTICADO À INSTÂNCIA DO FORMULÁRIO ---
        # O @login_required garante que request.user é um objeto User (não AnonymousUser).
        # Atribuímos ao campo 'usuario' do modelo Review ANTES de chamar form.is_valid().
        # form.instance é a instância do modelo que o formulário está construindo.
        form.instance.usuario = request.user

        # O formulário.is_valid() dispara as validações dos campos (incluindo Min/Max/Regex do modelo)
        # e também validações customizadas definidas no formulário (se houver).
        if form.is_valid():
            # O formulário está válido e form.instance.usuario já está definido
            # form.save() irá salvar a instância do modelo (review) no banco de dados.
            review = form.save()

            # --- RESPOSTA PARA REQUISIÇÃO AJAX (handled by make_review.js) ---
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                # Sucesso: Retorna JsonResponse indicando sucesso e uma URL de redirecionamento
                # Assumindo que a review salva tem um professor associado (campo required no modelo)
                # Usamos review.professor.id para gerar a URL da página de reviews do professor
                # Certifique-se de que 'reviews:professor_reviews' é o nome da URL pattern correta
                try:
                    # Verifica se review.professor é None antes de tentar acessar review.professor.id
                    if review.professor:
                         # Gera a URL para a página do professor específico
                         professor_page_url = reverse('reviews:professor_reviews', args=[review.professor.id])
                         return JsonResponse({'success': True, 'message': 'Review enviado com sucesso!', 'redirect_url': professor_page_url})
                    else:
                         # Caso não haja professor salvo (improvável se o campo for required no modelo/form)
                         print("Erro lógico: Review salva sem professor associado.")
                         # Retorne sucesso, mas redirecione para uma página padrão (ex: lista de professores)
                         # Substitua 'universities:all_professors' pelo nome da URL pattern correta se for diferente
                         # Certifique-se que 'universities:all_professors' existe e está nomeada corretamente
                         try:
                              default_redirect_url = reverse('universities:all_professors')
                              return JsonResponse({'success': True, 'message': 'Review enviado com sucesso!', 'redirect_url': default_redirect_url})
                         except Exception as url_err:
                              print(f"Erro ao gerar URL de redirecionamento padrão: {url_err}")
                              return JsonResponse({'success': True, 'message': 'Review enviado com sucesso, mas houve um problema ao redirecionar.', 'redirect_url': None})

                except Exception as e:
                    # Se algo der errado ao gerar a URL de redirecionamento, ainda retorne sucesso
                    # mas com uma mensagem de erro e talvez sem redirecionamento.
                    print(f"Erro inesperado ao gerar URL de redirecionamento após salvar review {review.id}: {e}") # Logar erro no servidor
                    return JsonResponse({'success': True, 'message': 'Review enviado com sucesso, mas houve um problema ao redirecionar.', 'redirect_url': None})


            # --- RESPOSTA PARA SUBMISSÃO TRADICIONAL (fallback, se JS estiver desabilitado) ---
            else:
                # Redireciona o navegador
                if review.professor:
                    # Ajuste o nome da URL e args conforme necessário
                    return redirect('reviews:professor_reviews', professor_id=review.professor.id)
                else:
                    # Ajuste a URL padrão
                    return redirect('universities:all_professors')

        else:
            # --- FORMULÁRIO INVÁLIDO ---
            # Handle requisição AJAX com formulário inválido
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                # Retorna JsonResponse com os erros do formulário
                # form.errors é um dicionário onde chaves são nomes de campos e valores são listas de strings de erro
                # O status 400 é CRUCIAL para o JavaScript entender que é um erro de validação
                # Incluímos `success: False` para clareza, embora o status 400 já indique falha
                return JsonResponse({'success': False, 'errors': form.errors}, status=400)

            # Handle submissão tradicional com formulário inválido
            else:
                # Continua para renderizar o template ABAIXO com o formulário contendo os erros
                # O template make_review.html já sabe como exibir form.errors
                pass # Nada mais precisa ser feito aqui, o código continua


    # O código só chega aqui se a requisição for GET, ou POST inválido tradicional
    # --- CONTEXTO PARA RENDERIZAÇÃO DO TEMPLATE (usado por GET e POST inválido tradicional) ---
    # O template make_review.html precisa do objeto 'form' e dados para os selects de Professor e Disciplina
    # Os dados para selects de Professor e Disciplina são necessários para renderizar as opções do <select>
    # usando {{ form.professor }} e {{ form.disciplina }} no template.
    # NOTA: Ao renderizar um formulário com POST inválido, o objeto 'form' já contém os dados
    # submetidos pelo usuário e os erros. Django preenche os selects automaticamente com
    # os dados do formulário.
    # Não precisamos buscar professores e disciplinas separadamente AQUI se estivermos
    # usando os widgets padrão do Django para esses campos.
    # Se você usar widgets customizados ou precisar de dados extras, pode buscá-los aqui.

    # Se você está usando o widget padrão de Select no Django (que renderiza <select><option>...</option></select>)
    # para os campos Professor e Disciplina, o Django já se encarrega de popular as opções
    # usando os objetos relacionados (Professor.objects.all(), Disciplina.objects.all())
    # a partir do campo no form (ForeignKey). Você não precisa passá-los explicitamente no contexto
    # a menos que precise *filtrar* ou *ordenar* essas opções de forma customizada ANTES
    # de renderizar o formulário.

    # Se a requisição for GET, crie um formulário vazio
    if request.method == 'GET':
         form = ReviewForm()

    # O contexto mínimo necessário é apenas o objeto form.
    context = {
        'form': form, # Passa o objeto form (com erros se for POST inválido, ou vazio se for GET)
    }

    # Renderiza o template make_review.html com o contexto
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