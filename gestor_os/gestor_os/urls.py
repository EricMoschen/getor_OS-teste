from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("cadastro/", include("cadastro.urls")),
    path('', include('menu.urls')),
    path('lancamento/', include("lancamento.urls")),
]
