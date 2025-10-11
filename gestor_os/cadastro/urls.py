from django.urls import path
from . import views

urlpatterns = [
    path("centro-custo/", views.cadastrar_centro_custo, name='cadastrar_centro_custo'),
    
    path("cliente/", views.cadastro_cliente, name="cadastro_cliente"),
    path("cliente/excluir/<int:pk>/", views.excluir_cliente, name="excluir_cliente"),

    path('intervencao/', views.cadastro_intervencao, name='cadastro_intervencao'),
    path('intervencao/excluir/<int:pk>/', views.excluir_intervencao, name='excluir_intervencao'),
    
    path('colaborador/', views.cadastro_colaborador, name='cadastro_colaborador'),
    path('colaborador/excluir/<int:pk>/', views.excluir_colaborador, name='excluir_colaborador'),
]