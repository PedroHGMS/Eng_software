from django.urls import path
from reviews import views

app_name = "reviews"
urlpatterns = [
    path("all_reviews/", views.all_reviews, name="all_reviews"),
    path("single_professor_reviews/<int:professor_id>/", views.single_professor_reviews, name="single_professor_reviews"),
    path('search/', views.search_reviews, name='search_reviews'),
]
