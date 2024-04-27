from django.contrib import admin
from django.urls import path
from api.users import views
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView

# TODO:s 13, 16, 18, 19
urlpatterns = [

    path('admin/', admin.site.urls),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    path('api/users/', views.RegistroView.as_view(), name='registro'),
    path('api/users/login/', views.LoginView.as_view(), name='login'),
    path('api/users/me/', views.UsuarioView.as_view(), name='usuario-me'),
    path('api/users/logout/', views.LogoutView.as_view(), name='logout'),
    path('api/peliculas/', views.PeliculaCreateView.as_view(), name='pelicula-list-create'),
    path('api/peliculas/<int:pk>/', views.PeliculaDetailView.as_view(), name='pelicula-detail'),
    path('api/reviews/', views.ReviewListCreateView.as_view(), name='review-list-create'),
]
