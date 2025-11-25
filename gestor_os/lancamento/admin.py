from django.contrib import admin
from .models import Colaborador, AberturaOS, CentroCusto, Cliente, Intervencao, ApontamentoHoras


@admin.register(Colaborador)
class ColaboradorAdmin(admin.ModelAdmin):
    list_display = ("matricula", "nome", "funcao", "turno",)
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

# Caso esses modelos existam e você queira administrá-los também:
@admin.register(ApontamentoHoras)
class ApontamentoHorasAdmin(admin.ModelAdmin):
    list_display = ("colaborador", "ordem_servico", "data_inicio", "data_fim" , "tipo_dia")
    search_fields = ("colaborador__nome", "ordem_servico__descricao", "data_inicio", "data_fim")
