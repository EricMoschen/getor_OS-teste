from django.urls import path
from . import views

urlpatterns = [
    path('', views.abrir_os, name='abrir_os'),
    path('editar/<int:pk>/', views.editar_os, name='editar_os'),
    path('excluir/<int:pk>/', views.excluir_os, name='excluir_os'),
]