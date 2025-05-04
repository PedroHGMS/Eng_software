from django.shortcuts import render

# Create your views here.
from .models import Professor


def all_professors(request):
    """
    View to display all professors.
    """
    Professors = Professor.objects.all()

    return render(request, rf"universities/all_professors.html", context={"professors": Professors})
