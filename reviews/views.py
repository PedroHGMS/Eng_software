from django.shortcuts import render

# Create your views here.
from .models import Review
from universities.models import Professor
from django.http import HttpResponse
from django.db.models import Q


# Loads the reviews from the database and renders them in the template
def all_reviews(request):
    # Get all reviews from the database
    reviews = Review.objects.all()
    
    # Render the reviews in the template
    return render(request, "reviews/all_reviews.html", {"reviews": reviews})

# Load only the reviews of a specific professor
def single_professor_reviews(request, professor_id):
    # Get the reviews of the specified professor
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