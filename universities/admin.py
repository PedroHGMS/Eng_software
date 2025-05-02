from django.contrib import admin

# Register your models here.
from .models import Professor
from .models import Universidade
from .models import Disciplina

admin.site.register(Professor)
admin.site.register(Universidade)
admin.site.register(Disciplina)