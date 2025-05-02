from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.
from .models import Professor

def all_professors(request):
    Professors = Professor.objects.all()

    return render(request, rf"universities/all_professors.html", context={"professors":Professors})
