from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.views.generic.base import RedirectView


urlpatterns = [
    path('admin/', admin.site.urls),
    path('universities/', include("universities.urls", namespace="universities")),
    path('reviews/', include("reviews.urls", namespace="reviews")),
    path('', include('users.urls')),
    path('', RedirectView.as_view(url='/login/', permanent=False), name='index_redirect'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
]
