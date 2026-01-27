from django.urls import path
from . import views

urlpatterns = [
    
    # Rota para finalizar os 
    path("finalizar-os/", views.finalizar_os, name="finalizar_os"),
    path("buscar-os/<str:numero_os>/", views.buscar_os),

]
