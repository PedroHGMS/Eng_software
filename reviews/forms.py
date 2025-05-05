# reviews/forms.py

from django import forms
from .models import Review
# Opcional: Importar outros modelos se precisar customizar campos relacionados
# from universities.models import Professor, Disciplina

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        # Liste todos os campos que vêm do input direto do usuário.
        # NÃO inclua 'usuario' aqui, pois ele será atribuído manualmente na view para o usuário logado.
        fields = ['dificuldade', 'qualidade', 'descricao', 'nota_obtida', 'presenca', 'periodo', 'professor', 'disciplina']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Adicionar classes CSS base para estilização no CSS
        for field_name, field in self.fields.items():
            # Adicionar uma classe comum 'form-control' para inputs, selects, textareas
            # Excluímos o checkbox 'presenca' explicitamente ou pelo tipo de widget
            # já que o CSS/JS customiza o visual dele de forma diferente.
            if not isinstance(field.widget, forms.CheckboxInput):
                 field.widget.attrs.update({'class': 'form-control'})

            # Adicionar atributos HTML específicos para validação/UX onde apropriado
            if field_name in ['dificuldade', 'qualidade']:
                 field.widget.attrs.update({'min': 1, 'max': 5}) # Garante que o input subjacente tenha min/max
            elif field_name == 'nota_obtida':
                 # Adiciona min, max (ajuste conforme seu modelo e requisitos) e step
                 field.widget.attrs.update({'min': 0, 'max': 100, 'step': 'any'}) # Exemplo: 0 a 10, qualquer decimal
            elif field_name == 'descricao':
                 field.widget.attrs.update({'rows': 4}) # Altura padrão para textarea