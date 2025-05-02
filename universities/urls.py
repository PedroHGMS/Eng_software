from django.urls import path
from universities import views

app_name = "universities"
urlpatterns = [
    path("all_professors/", views.all_professors, name="all_professors"),
]