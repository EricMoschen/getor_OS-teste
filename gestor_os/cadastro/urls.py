from django.urls import path
from . import views

urlpatterns = [
    path("centro-custo/", views.cadastrar_centro_custo, name='cadastrar_centro_custo'),
]