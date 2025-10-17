from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path('', include('menu.urls')),
    path("cadastro/", include('cadastro.urls')),
    path('lancamento/', include('lancamento.urls')),
]
