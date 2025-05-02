from django.urls import path
from universities import views

urlpatterns = [
    path("index/", views.index, name="index"),
]