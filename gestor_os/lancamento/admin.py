from django.contrib import admin
from .models import Colaborador, AberturaOS, CentroCusto, Cliente, Intervencao


@admin.register(Colaborador)
class ColaboradorAdmin(admin.ModelAdmin):
    list_display = ("matricula", "nome", "funcao", "turno")
    search_fields = ("matricula", "nome")
    list_filter = ("turno",)


@admin.register(AberturaOS)
class AberturaOSAdmin(admin.ModelAdmin):
    list_display = ("numero_os", "descricao_os", "cliente", "centro_custo", "situacao", "data_abertura")
    search_fields = ("numero_os", "descricao_os")
    list_filter = ("situacao", "cliente", "centro_custo")


# Caso esses modelos existam e você queira administrá-los também:
@admin.register(CentroCusto)
class CentroCustoAdmin(admin.ModelAdmin):
    list_display = ("descricao",)
    search_fields = ("descricao",)


