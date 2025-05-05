from django.shortcuts import render
from django.contrib.auth.decorators import login_required

# Create your views here.
from .models import Professor

@login_required
def all_professors(request):
    """
    View to display all professors.
    """
    Professors = Professor.objects.all()

    return render(request, "universities/all_professors.html", context={"professors": Professors})
