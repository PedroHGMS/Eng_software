from django import forms
from .models import Review
from universities.models import Professor, Disciplina
from django.contrib.auth.models import User

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['dificuldade', 'qualidade', 'descricao', 'nota_obtida', 'presenca', 'periodo', 'professor', 'disciplina']
    
    # Override the __init__ method to reorder fields
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Reorder fields manually: switch 'dificuldade' and 'qualidade'
        self.fields['dificuldade'], self.fields['qualidade'] = self.fields['qualidade'], self.fields['dificuldade']
        
        # Add the user field as needed
        self.fields['user'] = forms.CharField(initial='guest', widget=forms.HiddenInput())
