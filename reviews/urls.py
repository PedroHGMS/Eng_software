from django.urls import path
from reviews import views

app_name = "reviews"
urlpatterns = [
    path("all_reviews/", views.all_reviews, name="all_reviews"),
    path("professor_reviews/<int:professor_id>/", views.professor_reviews_view, name="professor_reviews"),
]