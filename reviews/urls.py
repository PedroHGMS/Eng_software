from reviews import views
from django.views.generic.base import RedirectView
from django.urls import path, reverse_lazy

app_name = "reviews"
urlpatterns = [
    path("all_reviews/", views.all_reviews, name="all_reviews"),
    path("professor_reviews/<int:professor_id>/", views.professor_reviews_view, name="professor_reviews"),
    path('search/', views.search_reviews, name='search_reviews'),
    path('make_review/', views.MakeReview, name='make_review'),
    path('make_review/success/', views.MakeReviewSucess, name='success'),
]
