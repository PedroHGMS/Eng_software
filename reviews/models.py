from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User

# Create your models here.
class Review(models.Model):
    # Dificuldade, Qualidade, Descrição, Nota obtida, Presença e Período
    
    # Dificuldade só pode ser um desses valores [1, 2, 3, 4, 5]. 
    dificuldade = models.IntegerField(null=False, validators=[MinValueValidator(1), MaxValueValidator(5)])

    # Qualidade é um des valores [1, 2, 3, 4, 5]
    qualidade = models.IntegerField(null=False, validators=[MinValueValidator(1), MaxValueValidator(5)])

    # Descrição é um texto livre
    descricao = models.TextField(null=False)

    # Nota obtida é um inteiro de 0 a 100
    nota_obtida = models.IntegerField(null=False, validators=[MinValueValidator(0), MaxValueValidator(100)])

    # Presença é um booleano
    presenca = models.BooleanField(null=False, default=False)

    # Período deve estar no formato "ano/semestre", exemplo: "2023/1" ou "2023/2" ou "2024/2". Use regex para validar o formato.
    def validate_periodo(value):
        import re
        pattern = r'^\d{4}/[1-2]$'
        if not re.match(pattern, value):
            raise ValidationError(
                f'{value} não é um período válido. O formato deve ser "ano/semestre", exemplo: "2023/1" ou "2023/2" ou "2024/2".'
            )
    periodo = models.CharField(max_length=7, null=False, validators=[validate_periodo])

    # Relacionamentos com a review. Professor, Disciplina e Usuário.
    # Importa o professor

    # Cada review deve ter um professor
    professor = models.ForeignKey('universities.Professor', on_delete=models.CASCADE, null=False, blank=False)

    # Cada review deve ter uma disciplina
    disciplina = models.ForeignKey('universities.disciplina', on_delete=models.CASCADE, null=False, blank=False)

    # Cada review deve ter um usuário sem ser admin
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    
    def __str__(self):
        return f"Review de {self.usuario} para {self.professor} em {self.disciplina}"



