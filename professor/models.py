from django.db import models

class Professor(models.Model):
    name = models.CharField(max_length=255, null=False)
    departamento = models.CharField(max_length=255, null=False, default="Ciência da Computação")

class Universidade(models.Model):
    nome = models.CharField(max_length=255, null=False)
    professores = models.ManyToManyField(Professor, related_name='universidades')