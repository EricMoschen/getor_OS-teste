from django.urls import path
from . import views

urlpatterns = [
    path("centro-custo/", views.cadastrar_centro_custo, name='cadastrar_centro_custo'),
    path("cliente/", views.cadastro_cliente, name='cadastro_cliente'),
]