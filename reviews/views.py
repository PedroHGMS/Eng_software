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


def single_professor_reviews(request, professor_id):
    reviews = Review.objects.filter(professor_id=professor_id)
    professor = Professor.objects.get(id=professor_id)

    return render(request, "reviews/single_professor_reviews.html", {"reviews": reviews, "professor": professor})


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
