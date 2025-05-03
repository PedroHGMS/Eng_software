from django.shortcuts import render

from .models import Review
from universities.models import Professor
from django.http import HttpResponse

def all_reviews(request):
    reviews = Review.objects.all()
    return render(request, "reviews/reviews.html", {"reviews": reviews})

def single_professor_reviews(request, professor_id):
    reviews = Review.objects.filter(professor_id=professor_id)
    professor = Professor.objects.get(id=professor_id)
    return render(request, "reviews/single_professor_reviews.html", {"reviews": reviews, "professor": professor})