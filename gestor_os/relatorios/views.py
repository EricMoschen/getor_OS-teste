from collections import defaultdict
from datetime import datetime, timedelta, time

import holidays
from django.conf import settings
from django.db.models import Q
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.dateparse import parse_date
from weasyprint import HTML

from lancamento.models import AberturaOS, ApontamentoHoras
from .utils import gerar_proximo_orcamento, montar_dados_log_os
from gestor_os.access import RELATORIOS_GROUP, group_required

# =====================================================
# CONSTANTES
# =====================================================

BR_HOLIDAYS = holidays.Brazil()


# =====================================================
# UTILITÁRIOS
# =====================================================

def formatar_horas(horas: float) -> str:
    if not horas or horas <= 0:
        return "00:00"
    h = int(horas)
    m = int(round((horas - h) * 60))
    return f"{h:02d}:{m:02d}"


def aplicar_filtro_datas(queryset, data_inicio, data_fim):
    if data_inicio and data_fim:
        return queryset.filter(
            data_inicio__lte=datetime.combine(data_fim, time.max),
            data_fim__gte=datetime.combine(data_inicio, time.min),
        )
    if data_inicio:
        return queryset.filter(data_fim__gte=datetime.combine(data_inicio, time.min))
    if data_fim:
        return queryset.filter(data_inicio__lte=datetime.combine(data_fim, time.max))
    return queryset


# =====================================================
# FINALIZAR OS
# =====================================================
@login_required
@group_required(RELATORIOS_GROUP)
def finalizar_os(request):
    ordens = AberturaOS.objects.all().order_by("-numero_os")

    if request.method == "POST":
        numero_os = request.POST.get("numero_os_hidden")
        observacoes = request.POST.get("observacoes", "").strip()

        if not observacoes:
            return render(request, "finalizar_os/finalizar_os.html", {
                "ordens": ordens,
                "erro": "Informe a observação antes de finalizar a OS."
            })

        os_obj = get_object_or_404(AberturaOS, numero_os=numero_os)
        os_obj.observacoes = observacoes
        os_obj.situacao = "FI"
        os_obj.save()

        return redirect("finalizar_os")

    return render(request, "finalizar_os/finalizar_os.html", {"ordens": ordens})


# =====================================================
# BUSCAR OS (AJAX)
# =====================================================
@login_required
@group_required(RELATORIOS_GROUP)
def buscar_os(request, numero_os):
    try:
        os_obj = AberturaOS.objects.get(numero_os=numero_os)
        return JsonResponse({
            "descricao": os_obj.descricao_os,
            "situacao": os_obj.get_situacao_display(),
            "observacoes": os_obj.observacoes or ""
        })
    except AberturaOS.DoesNotExist:
        return JsonResponse({"erro": True})


# =====================================================
# CÁLCULO DE HORAS
# =====================================================

def calcular_horas(inicio, fim, colaborador):
    inicio = timezone.localtime(inicio)
    fim = timezone.localtime(fim)

    if fim <= inicio:
        fim += timedelta(days=1)

    data_base = inicio.date()
    total_horas = (fim - inicio).total_seconds() / 3600

    # Domingo ou feriado
    if inicio.weekday() == 6 or data_base in BR_HOLIDAYS:
        return 0, 0, total_horas

    # Sábado
    if inicio.weekday() == 5:
        return 0, total_horas, 0

    blocos = []
    almoco = None
    turno = colaborador.turno

    if turno == "A":
        blocos = [(7, 0, 11, 0), (12, 0, 16, 48)]
        almoco = (11, 0, 12, 0)

    elif turno == "HC":
        blocos = [(8, 0, 12, 0), (13, 0, 17, 48)]
        almoco = (12, 0, 13, 0)

    elif turno == "B":
        blocos = [(16, 48, 19, 0), (20, 0, 26, 0)]

    elif turno == "OUTROS":
        if colaborador.hr_entrada_am and colaborador.hr_saida_am:
            blocos.append((
                colaborador.hr_entrada_am.hour,
                colaborador.hr_entrada_am.minute,
                colaborador.hr_saida_am.hour,
                colaborador.hr_saida_am.minute
            ))

        if colaborador.hr_entrada_pm and colaborador.hr_saida_pm:
            blocos.append((
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

    blocos_turno = []
    for h1, m1, h2, m2 in blocos:
        ini = timezone.make_aware(datetime.combine(data_base, time(h1 % 24, m1)))
        fim_t = timezone.make_aware(datetime.combine(data_base, time(h2 % 24, m2)))
        if h2 >= 24:
            fim_t += timedelta(days=1)
        blocos_turno.append((ini, fim_t))

    horas_normais = 0
    blocos_trabalhados = []

    for ini_t, fim_t in blocos_turno:
        ini_real = max(inicio, ini_t)
        fim_real = min(fim, fim_t)
        if ini_real < fim_real:
            horas_normais += (fim_real - ini_real).total_seconds() / 3600
            blocos_trabalhados.append((ini_real, fim_real))

    horas_extras = 0
    cursor = inicio
    blocos_trabalhados.sort()

    for ini_b, fim_b in blocos_trabalhados:
        if cursor < ini_b:
            horas_extras += (ini_b - cursor).total_seconds() / 3600
        cursor = max(cursor, fim_b)

    if cursor < fim:
        horas_extras += (fim - cursor).total_seconds() / 3600

    if almoco:
        ah1, am1, ah2, am2 = almoco
        alm_ini = timezone.make_aware(datetime.combine(data_base, time(ah1, am1)))
        alm_fim = timezone.make_aware(datetime.combine(data_base, time(ah2, am2)))
        ini = max(inicio, alm_ini)
        fim_i = min(fim, alm_fim)
        if ini < fim_i:
            horas_extras -= (fim_i - ini).total_seconds() / 3600

    horas_extras = max(0, min(horas_extras, total_horas - horas_normais))
    return horas_normais, horas_extras, 0


# =====================================================
# PROCESSAR RELATÓRIO
# =====================================================
def processar_relatorio(apontamentos):

    colaboradores = defaultdict(lambda: {
        "matricula": "",
        "nome": "",
        "normais": 0,
        "extra50": 0,
        "extra100": 0,
    })

    # =========================
    # AGRUPAR APONTAMENTOS
    # =========================
    for ap in apontamentos:

        if not ap.data_inicio or not ap.data_fim:
            continue

        normais, extra50, extra100 = calcular_horas(
            ap.data_inicio,
            ap.data_fim,
            ap.colaborador
        )

        col = colaboradores[ap.colaborador.id]

        col["matricula"] = ap.colaborador.matricula
        col["nome"] = ap.colaborador.nome

        col["normais"] += normais
        col["extra50"] += extra50
        col["extra100"] += extra100

    # =========================
    # MONTAR RELATÓRIO
    # =========================
    relatorio = []

    totais = {
        "normais": 0,
        "extra50": 0,
        "extra100": 0,
        "geral": 0
    }

    for c in colaboradores.values():

        total = c["normais"] + c["extra50"] + c["extra100"]

        totais["normais"] += c["normais"]
        totais["extra50"] += c["extra50"]
        totais["extra100"] += c["extra100"]
        totais["geral"] += total

        relatorio.append({
            "matricula": c["matricula"],
            "nome": c["nome"],
            "horas_normais_fmt": formatar_horas(c["normais"]),
            "horas_50_fmt": formatar_horas(c["extra50"]),
            "horas_100_fmt": formatar_horas(c["extra100"]),
            "total_fmt": formatar_horas(total),
        })

    # =========================
    # FORMATAR TOTAIS
    # =========================
    totais_formatados = {
        "normais": formatar_horas(totais["normais"]),
        "extra50": formatar_horas(totais["extra50"]),
        "extra100": formatar_horas(totais["extra100"]),
        "geral": formatar_horas(totais["geral"]),
    }

    return relatorio, totais_formatados



# =====================================================
# RELATÓRIO OS
# =====================================================

def construir_contexto_relatorio_os(request):

    numero_os = request.GET.get("os")
    data_inicio = parse_date(request.GET.get("data_inicio") or "")
    data_fim = parse_date(request.GET.get("data_fim") or "")

    ordem_servico = None
    relatorio = []
    totais = None

    apontamentos = ApontamentoHoras.objects.select_related(
        "colaborador",
        "ordem_servico"
    )

    if numero_os:

        ordem_servico = get_object_or_404(AberturaOS, numero_os=numero_os)

        apontamentos = apontamentos.filter(ordem_servico=ordem_servico)

    if data_inicio:
        apontamentos = apontamentos.filter(
            data_fim__gte=datetime.combine(data_inicio, time.min)
        )

    if data_fim:
        apontamentos = apontamentos.filter(
            data_inicio__lte=datetime.combine(data_fim, time.max)
        )

    if apontamentos.exists():
        relatorio, totais = processar_relatorio(apontamentos)

    context = {
        "os_detalhes": ordem_servico,
        "relatorio": relatorio,
        "totais": totais,
        "filtro_os": numero_os,
        "data_inicio" : data_inicio,
        "data_fim": data_fim,
    }
    return context

@login_required
@group_required(RELATORIOS_GROUP)
def relatorio_os(request):

    context = construir_contexto_relatorio_os(request)

    return render(request, "relatorio_os/relatorio_os.html", context)
@login_required
@group_required(RELATORIOS_GROUP)
def orcamento_pdf(request):

    context = construir_contexto_relatorio_os(request)

    return render(request, "relatorio_os/orcamento_pdf.html", context)

# =====================================================
# ORÇAMENTO
# =====================================================
@login_required
@group_required(RELATORIOS_GROUP)
def proximo_orcamento(request):
    return JsonResponse({"numero": str(gerar_proximo_orcamento()).zfill(4)})


# =====================================================
# LOG OS
# =====================================================
@login_required
@group_required(RELATORIOS_GROUP)
def log_os(request, numero_os):
    return render(request, "relatorio_os/orcamento_detalhado.html",
                  montar_dados_log_os(numero_os))


# =====================================================
# PDF LOG OS
# =====================================================

@login_required
@group_required(RELATORIOS_GROUP)
def log_os_pdf(request, numero_os):
    os_obj = get_object_or_404(AberturaOS, numero_os=numero_os)

    data_inicio = parse_date(request.GET.get("data_inicio") or "")
    data_fim = parse_date(request.GET.get("data_fim") or "")

    apontamentos = ApontamentoHoras.objects.filter(ordem_servico=os_obj)
    apontamentos = aplicar_filtro_datas(apontamentos, data_inicio, data_fim)

    colabs = defaultdict(lambda: {"apontamentos": [], "total_segundos": 0})
    total_geral = 0

    for ap in apontamentos:
        duracao = (ap.data_fim - ap.data_inicio).total_seconds()
        if duracao <= 0:
            continue

        total_geral += duracao
        col = colabs[ap.colaborador]
        col["apontamentos"].append({
            "data": ap.data_inicio.strftime("%d/%m/%Y"),
            "inicio": ap.data_inicio.strftime("%H:%M"),
            "fim": ap.data_fim.strftime("%H:%M"),
            "duracao": formatar_horas(duracao / 3600),
            "servico": getattr(ap, "servico", "-"),
        })
        col["total_segundos"] += duracao

    colaboradores = [{
        "colaborador": c,
        "apontamentos": v["apontamentos"],
        "total_fmt": formatar_horas(v["total_segundos"] / 3600)
    } for c, v in colabs.items()]

    html = render_to_string("relatorio_os/orcamento_detalhado.html", {
        "logo_path": request.build_absolute_uri("/static/img/logo.png"),
        "data_emissao": timezone.now().strftime("%d/%m/%Y %H:%M"),
        "os": os_obj,
        "colaboradores": colaboradores,
        "total_geral": formatar_horas(total_geral / 3600),
    })

    pdf = HTML(string=html, base_url=request.build_absolute_uri()).write_pdf()
    return HttpResponse(pdf, content_type="application/pdf")
