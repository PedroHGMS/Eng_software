from django.urls import path
from reviews import views
from django.views.generic.base import RedirectView # Import RedirectView
from django.urls import path, include, reverse_lazy # Import reverse_lazy

app_name = "reviews"
urlpatterns = [
    path('', RedirectView.as_view(url=reverse_lazy('reviews:all_reviews'), permanent=False), name='home'),
    path("all_reviews/", views.all_reviews, name="all_reviews"),
    path("single_professor_reviews/<int:professor_id>/", views.single_professor_reviews, name="single_professor_reviews"),
    path('search/', views.search_reviews, name='search_reviews'),
    path('logout/', views.my_custom_logout_view, name='logout'),
]
