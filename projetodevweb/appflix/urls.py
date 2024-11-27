from django.contrib import admin
from django.urls import path
from appflix import views
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.home, name='home'),  # página inicial
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),  # página de login
    path('editar_perfil/', views.editar_perfil, name='editar_perfil'),
    path('minhas_reviews/', views.minhas_reviews, name='minhas_reviews'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),  # URL de logout
    path('register/', views.register, name='register'),  # página de registro
    path('filme/<str:filme_id>/', views.detalhes_filme, name='detalhes_filme'),  # URL de detalhes do filme
    path('filme/<int:filme_id>/adicionar_review/', views.adicionar_review, name='adicionar_review'),
]