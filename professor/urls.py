from django.urls import path
from professor import views

urlpatterns = [
    path("index/", views.index, name="index"),
]