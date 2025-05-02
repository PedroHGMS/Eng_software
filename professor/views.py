from django.shortcuts import render
from django.http import HttpResponse
from .models import Professor

def index(request):
    Professors = Professor.objects.get(id=1)
    print(Professors.name)
    print("oi")
    return render(request, rf"professor/example.html", context={"professor":Professors})
