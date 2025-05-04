from django.shortcuts import render
from django.db.models import Avg, Count, Case, When, BooleanField, Value as V
from .models import Review
from universities.models import Professor, Universidade, Disciplina
from django.http import HttpResponse
from django.db.models import Q


def all_reviews(request):
    professors = Professor.objects.annotate(
        avg_rate=Avg("review__qualidade"),
        total_reviews=Count("review", distinct=True),
        total_subjects=Count("review__disciplina", distinct=True)
    ).filter(total_reviews__gt=0).order_by("?")

    top_disciplinas = Disciplina.objects.annotate(
    qualidade_media=Avg("review__qualidade"),
    total_avaliacoes=Count("review")
    ).filter(total_avaliacoes__gt=0).order_by("-qualidade_media")[:5]

    top_universidades = Universidade.objects.annotate(
        qualidade_media=Avg("professor__review__qualidade"),
        total_avaliacoes=Count("professor__review")
    ).filter(total_avaliacoes__gt=0).order_by("-qualidade_media")[:5]

    return render(request, "reviews/reviews.html", {
        "professors": professors,
        "top_disciplinas": top_disciplinas,
        "top_universidades": top_universidades,
    })

def single_professor_reviews(request, professor_id):
    reviews = Review.objects.filter(professor_id=professor_id)
    professor = Professor.objects.get(id=professor_id)

    # Render the reviews in the template
    return render(request, "reviews/single_professor_reviews.html", {"reviews": reviews, "professor": professor})

def search_reviews(request):
    query = request.GET.get('q', '')
    results = []

    if query:
        results = Review.objects.filter(
            Q(professor__name__icontains=query) |  # professor name
            Q(disciplina__nome__icontains=query) |  # discipline name
            Q(descricao__icontains=query)           # review description
        ).distinct()

    return render(request, 'reviews/search_results.html', {
        'query': query,
        'results': results
    })
