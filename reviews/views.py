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

    # Render the reviews in the template
    return render(request, "reviews/single_professor_reviews.html", {"reviews": reviews, "professor": professor})


def search_reviews(request):
    query = request.GET.get('q', '').strip()
    # Initialize professors_found as an empty queryset
    professors_found = Professor.objects.none()

    if query:
        # 1. Find reviews matching the query criteria
        matching_reviews = Review.objects.filter(
            Q(professor__name__icontains=query) |
            Q(disciplina__nome__icontains=query) |
            Q(descricao__icontains=query)
        ).distinct() # Find distinct reviews first

        # 2. Get the unique IDs of the professors from these reviews
        professor_ids = matching_reviews.values_list('professor_id', flat=True).distinct()

        # 3. Retrieve the actual Professor objects based on those IDs
        if professor_ids:
            professors_found = Professor.objects.filter(id__in=professor_ids).order_by('name') # Order alphabetically

    # 4. Pass the queryset of unique PROFESSORS to the template
    return render(request, 'reviews/search_results.html', {
        'query': query,
        'professors_found': professors_found # Pass professors instead of reviews
    })

def my_custom_logout_view(request):
    logout(request)
    # Redirect to a page after logout
    return redirect('/') # Or wherever you want them to go