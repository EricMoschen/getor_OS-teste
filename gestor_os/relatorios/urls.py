from django.urls import path
from . import views

urlpatterns = [
    
    # Rota para finalizar os 
    path("finalizar-os/", views.finalizar_os, name="finalizar_os"),
    path("buscar-os/<str:numero_os>/", views.buscar_os),

    # Rota para Relatorios OS
    path("relatorio-os/", views.relatorio_os, name="relatorio_os"),


    path("proximo_orcamento/", views.proximo_orcamento, name="proximo_orcamento"),

]
