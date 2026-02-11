from django.urls import path
from . import views

urlpatterns = [
    path('', views.abrir_os, name='abrir_os'),
    path('editar_os/<int:pk>/', views.editar_os, name='editar_os'),
    path('excluir/<int:pk>/', views.excluir_os, name='excluir_os'),
    path('get_subcentros/', views.get_subcentros, name='get_subcentros'),

    # impressão de OS
    path('imprimir_os/<int:pk>/', views.imprimir_os, name='imprimir_os'),

    # apontamento de horas
    path("apontar_horas/", views.apontar_horas, name="apontar_horas"),
    path("api/colaborador/<str:matricula>/", views.api_colaborador, name="api_colaborador"),
    path("api/os/<str:numero>/", views.api_os, name="api_os"),
    path("api/os/detalhes/<int:pk>/", views.api_os_detalhes, name="api_os_detalhes"),


    path("ajuste_horas/", views.ajuste_horas_supervisor, name="ajuste_horas_supervisor"),
]
