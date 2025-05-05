# users/urls.py
from django.urls import path
# Importar as views
from .views import login_view, register_view, logout_view # Adicionado register_view e logout_view

app_name = 'users' # Define um namespace para as URLs deste app

urlpatterns = [
    path('login/', login_view, name='login'),
    path('register/', register_view, name='register'), # Adiciona a URL para cadastro
    path('logout/', logout_view, name='logout'), # Adiciona a URL para logout (opcional)
]