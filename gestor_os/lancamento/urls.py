from django.urls import path
from . import views

urlpatterns = [
    path('', views.abrir_os, name='abrir_os'),
    path('editar_os/<int:pk>/', views.editar_os, name='editar_os'),
    path('excluir/<int:pk>/', views.excluir_os, name='excluir_os'),
    path('get_subcentros/', views.get_subcentros, name='get_subcentros'),

    # impressão de OS
    path('imprimir_os/<int:pk>/', views.imprimir_os, name='imprimir_os'),
]
