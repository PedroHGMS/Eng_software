from django.shortcuts import render
from django.db.models import Avg, Count
from .models import Review
from universities.models import Professor
from django.http import HttpResponse
from django.db.models import Q


def all_reviews(request):
    professors = Professor.objects.annotate(
        avg_rate=Avg("review__qualidade"),
        total_reviews=Count("review", distinct=True),
        total_subjects=Count("review__disciplina", distinct=True)
    ).filter(total_reviews__gt=0)

    return render(request, "reviews/reviews.html", {"professors": professors})

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
