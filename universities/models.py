from django.db import models


# Create your models here.
class Professor(models.Model):
    name = models.CharField(max_length=255, null=False)
    departamento = models.CharField(max_length=255, null=False, default="Ciência da Computação")

    # Add a many to one relationship to Professor. A professor can belong to one university and a university can have many professors./
    universidade = models.ForeignKey('Universidade', on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.name


class Universidade(models.Model):
    nome = models.CharField(max_length=255, null=False)

    def __str__(self):
        return self.nome


class Disciplina(models.Model):
    nome = models.CharField(max_length=255, null=False)
    carga_horaria = models.IntegerField(null=False)
    universidades = models.ManyToManyField(Universidade, blank=True)

    def __str__(self):
        return self.nome
