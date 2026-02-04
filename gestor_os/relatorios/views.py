from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.conf import settings
from django.utils import timezone
from django.db.models import F

from lancamento.models import AberturaOS, ApontamentoHoras

from datetime import datetime, timedelta, time
from collections import defaultdict
import holidays
import io
import os




# =====================================================
# Finalizar OS
# =====================================================
def finalizar_os(request):
    ordens = AberturaOS.objects.all().order_by("-numero_os")

    if request.method == "POST":
        numero_os = request.POST.get("numero_os_hidden")
        observacoes = request.POST.get("observacoes", "").strip()

        # Verifica se a observação foi informada
        if not observacoes:
            return render(request, "finalizar_os/finalizar_os.html", {
                "ordens": ordens,
                "erro": "Informe a observação antes de finalizar a OS."
            })

        try:
            os = AberturaOS.objects.get(numero_os=numero_os)
            os.observacoes = observacoes  # Salva a observação diretamente na OS
            os.situacao = "FI"            # Marca como finalizada
            os.save()

            return redirect("finalizar_os")

        except AberturaOS.DoesNotExist:
            return render(request, "finalizar_os/finalizar_os.html", {
                "ordens": ordens,
                "erro": "OS não encontrada."
            })

    # GET → renderiza tela normalmente
    return render(request, "finalizar_os/finalizar_os.html", {
        "ordens": ordens
    })


# =====================================================
# Buscar OS via AJAX
# =====================================================
def buscar_os(request, numero_os):
    try:
        os = AberturaOS.objects.get(numero_os=numero_os)
        return JsonResponse({
            "descricao": os.descricao_os,
            "situacao": os.get_situacao_display(),
            "observacoes": os.observacoes or ""
        })
    except AberturaOS.DoesNotExist:
        return JsonResponse({"erro": True})





# =====================================================
# Relátorios OS 
# =====================================================

br_holidays = holidays.Brazil()
def calcular_horas(inicio, fim, colaborador):
    inicio = timezone.localtime(inicio)
    fim = timezone.localtime(fim)

    if fim < inicio:
        fim += timedelta(days=1)

    data_base = inicio.date()
    total_horas = (fim - inicio).total_seconds() / 3600

    # =========================
    # DOMINGO / FERIADO → 100%
    # =========================
    if data_base in br_holidays or inicio.weekday() == 6:
        return 0, 0, total_horas

    # =========================
    # SÁBADO → 50%
    # =========================
    if inicio.weekday() == 5:
        return 0, total_horas, 0

    turno = colaborador.turno
    blocos_validos = []
    almoco = None

    # =========================
    # TURNOS FIXOS
    # =========================
    if turno == "A":
        blocos_validos = [(7, 0, 11, 0), (12, 0, 16, 48)]
        almoco = (11, 0, 12, 0)

    elif turno == "HC":
        blocos_validos = [(8, 0, 12, 0), (13, 0, 17, 48)]
        almoco = (12, 0, 13, 0)

    elif turno == "B":
        blocos_validos = [(16, 48, 19, 0), (20, 0, 26, 0)]

    elif turno == "OUTROS":
        if colaborador.hr_entrada_am and colaborador.hr_saida_am:
            blocos_validos.append((
                colaborador.hr_entrada_am.hour,
                colaborador.hr_entrada_am.minute,
                colaborador.hr_saida_am.hour,
                colaborador.hr_saida_am.minute
            ))

        if colaborador.hr_entrada_pm and colaborador.hr_saida_pm:
            blocos_validos.append((
                colaborador.hr_entrada_pm.hour,
                colaborador.hr_entrada_pm.minute,
                colaborador.hr_saida_pm.hour,
                colaborador.hr_saida_pm.minute
            ))

        if colaborador.hr_saida_am and colaborador.hr_entrada_pm:
            almoco = (
                colaborador.hr_saida_am.hour,
                colaborador.hr_saida_am.minute,
                colaborador.hr_entrada_pm.hour,
                colaborador.hr_entrada_pm.minute
            )

    # =========================
    # GERAR BLOCOS DATETIME
    # =========================
    blocos_turno = []

    for h1, m1, h2, m2 in blocos_validos:
        ini = timezone.make_aware(datetime.combine(data_base, time(h1 % 24, m1)))
        fim_t = timezone.make_aware(datetime.combine(data_base, time(h2 % 24, m2)))

        if h2 >= 24:
            fim_t += timedelta(days=1)

        blocos_turno.append((ini, fim_t))

    # =========================
    # CALCULAR HORAS NORMAIS
    # =========================
    horas_normais = 0
    blocos_trabalhados = []

    for ini_t, fim_t in blocos_turno:
        ini_real = max(inicio, ini_t)
        fim_real = min(fim, fim_t)

        if ini_real < fim_real:
            horas_normais += (fim_real - ini_real).total_seconds() / 3600
            blocos_trabalhados.append((ini_real, fim_real))

    # =========================
    # CALCULAR EXTRAS FORA DOS BLOCOS
    # =========================
    horas_extras = 0
    cursor = inicio

    blocos_trabalhados.sort()

    for ini_b, fim_b in blocos_trabalhados:
        if cursor < ini_b:
            horas_extras += (ini_b - cursor).total_seconds() / 3600
        cursor = max(cursor, fim_b)

    if cursor < fim:
        horas_extras += (fim - cursor).total_seconds() / 3600

    # =========================
    # REMOVER HORÁRIO DE ALMOÇO DAS EXTRAS
    # =========================
    if almoco:
        ah1, am1, ah2, am2 = almoco

        alm_ini = timezone.make_aware(datetime.combine(data_base, time(ah1, am1)))
        alm_fim = timezone.make_aware(datetime.combine(data_base, time(ah2, am2)))

        ini = max(inicio, alm_ini)
        fim_i = min(fim, alm_fim)

        if ini < fim_i:
            horas_extras -= (fim_i - ini).total_seconds() / 3600

    # =========================
    # TRAVA FINAL — NUNCA GERAR EXTRA ERRADO
    # =========================
    horas_extras = max(horas_extras, 0)
    horas_extras = min(horas_extras, total_horas - horas_normais)

    return horas_normais, horas_extras, 0



from django.http import JsonResponse
from .utils import gerar_proximo_orcamento


def proximo_orcamento(request):

    numero = gerar_proximo_orcamento()

    return JsonResponse({
        "numero": str(numero).zfill(4)
    })



from django.shortcuts import render
from django.utils import timezone

from lancamento.models import ApontamentoHoras, AberturaOS
from .utils import ler_numero_orcamento

def relatorio_os(request):

    os_numero = request.GET.get("os")
    data_inicio = request.GET.get("data_inicio")
    data_fim = request.GET.get("data_fim")

    os_detalhes = None

    # ======================================================
    # BASE QUERY
    # ======================================================
    apontamentos = ApontamentoHoras.objects.select_related(
        "colaborador",
        "ordem_servico"
    )

    # ======================================================
    # FILTRO POR OS
    # ======================================================
    if os_numero:
        apontamentos = apontamentos.filter(
            ordem_servico__numero_os=os_numero
        )

        os_obj = AberturaOS.objects.filter(
            numero_os=os_numero
        ).select_related("cliente").first()

        if os_obj:
            os_detalhes = {
                "numero": os_obj.numero_os,
                "descricao": os_obj.descricao_os,
                "cliente": str(os_obj.cliente),
                "codigo_cliente": getattr(os_obj.cliente, "codigo", "")
            }

    # ======================================================
    # FILTRO POR DATA
    # ======================================================
    if data_inicio:
        apontamentos = apontamentos.filter(
            data_inicio__date__gte=data_inicio
        )

    if data_fim:
        apontamentos = apontamentos.filter(
            data_fim__date__lte=data_fim
        )

    # ======================================================
    # AGRUPAMENTO POR COLABORADOR (TELA)
    # ======================================================
    agrupado_colaborador = {}

    # ======================================================
    # AGRUPAMENTO POR FUNÇÃO (PDF)
    # ======================================================
    agrupado_funcao = {}

    def fmt(valor):
        return f"{valor:.2f}".replace(".", ",")

    for ap in apontamentos:

        if not ap.data_fim:
            continue

        normais, h50, h100 = calcular_horas(
            ap.data_inicio,
            ap.data_fim,
            ap.colaborador
        )

        # ================================
        # AGRUPA POR COLABORADOR (TELA)
        # ================================
        colab = ap.colaborador
        chave_colab = colab.id

        if chave_colab not in agrupado_colaborador:
            agrupado_colaborador[chave_colab] = {
                "matricula": getattr(colab, "matricula", "-"),
                "nome": colab.nome,
                "horas_normais": 0,
                "horas_50": 0,
                "horas_100": 0,
            }

        agrupado_colaborador[chave_colab]["horas_normais"] += normais
        agrupado_colaborador[chave_colab]["horas_50"] += h50
        agrupado_colaborador[chave_colab]["horas_100"] += h100

        # ================================
        # AGRUPA POR FUNÇÃO (PDF)
        # ================================
        funcao = getattr(colab, "funcao", colab.nome)

        if funcao not in agrupado_funcao:
            agrupado_funcao[funcao] = {
                "funcao": funcao,
                "horas_normais": 0,
                "horas_50": 0,
                "horas_100": 0,
            }

        agrupado_funcao[funcao]["horas_normais"] += normais
        agrupado_funcao[funcao]["horas_50"] += h50
        agrupado_funcao[funcao]["horas_100"] += h100

    # ======================================================
    # CONVERTE → LISTA PARA TELA
    # ======================================================
    relatorio_individual = []

    for dados in agrupado_colaborador.values():

        total = (
            dados["horas_normais"]
            + dados["horas_50"]
            + dados["horas_100"]
        )

        relatorio_individual.append({
            "matricula": dados["matricula"],
            "nome": dados["nome"],

            "horas_normais": round(dados["horas_normais"], 2),
            "horas_50": round(dados["horas_50"], 2),
            "horas_100": round(dados["horas_100"], 2),

            "horas_normais_fmt": fmt(dados["horas_normais"]),
            "horas_50_fmt": fmt(dados["horas_50"]),
            "horas_100_fmt": fmt(dados["horas_100"]),
            "total_fmt": fmt(total),
        })

    # ======================================================
    # CONVERTE → LISTA PARA PDF
    # ======================================================
    relatorio_pdf = []

    for dados in agrupado_funcao.values():

        total = (
            dados["horas_normais"]
            + dados["horas_50"]
            + dados["horas_100"]
        )

        relatorio_pdf.append({
            "matricula": "-",
            "nome": dados["funcao"],

            "horas_normais": round(dados["horas_normais"], 2),
            "horas_50": round(dados["horas_50"], 2),
            "horas_100": round(dados["horas_100"], 2),

            "horas_normais_fmt": fmt(dados["horas_normais"]),
            "horas_50_fmt": fmt(dados["horas_50"]),
            "horas_100_fmt": fmt(dados["horas_100"]),
            "total_fmt": fmt(total),
        })

    # ======================================================
    # NÚMERO ORÇAMENTO
    # ======================================================
    numero_orcamento = str(
        ler_numero_orcamento()
    ).zfill(4)

    # ======================================================
    # EXPORTAR PDF
    # ======================================================
    if request.GET.get("export_pdf"):
        return render(request, "relatorio_os/orcamento_pdf.html", {
            "apontamentos": relatorio_pdf,
            "os": os_detalhes,
            "numero_orcamento": numero_orcamento,
            "data_atual": timezone.now().strftime("%d/%m/%Y"),
        })

    # ======================================================
    # RELATÓRIO NORMAL
    # ======================================================
    return render(request, "relatorio_os/relatorio_os.html", {
        "relatorio": relatorio_individual,
        "os_detalhes": os_detalhes,
    })
