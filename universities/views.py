from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.
from .models import Professor

def index(request):
    Professors = Professor.objects.get(id=1)

    return render(request, rf"university/example.html", context={"professor":Professors})
