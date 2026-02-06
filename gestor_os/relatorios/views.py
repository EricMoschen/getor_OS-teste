from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from django.utils.dateparse import parse_date
from django.conf import settings

from collections import defaultdict
from datetime import datetime, timedelta, time

import holidays
import os

from weasyprint import HTML
from django.template.loader import render_to_string

from lancamento.models import AberturaOS, ApontamentoHoras
from .utils import gerar_proximo_orcamento, montar_dados_log_os


# =====================================================
# FINALIZAR OS
# =====================================================

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

        try:
            os_obj = AberturaOS.objects.get(numero_os=numero_os)

            os_obj.observacoes = observacoes
            os_obj.situacao = "FI"
            os_obj.save()

            return redirect("finalizar_os")

        except AberturaOS.DoesNotExist:
            return render(request, "finalizar_os/finalizar_os.html", {
                "ordens": ordens,
                "erro": "OS não encontrada."
            })

    return render(request, "finalizar_os/finalizar_os.html", {"ordens": ordens})


# =====================================================
# BUSCAR OS AJAX
# =====================================================

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
# CALCULO DE HORAS
# =====================================================

br_holidays = holidays.Brazil()


def calcular_horas(inicio, fim, colaborador):

    inicio = timezone.localtime(inicio)
    fim = timezone.localtime(fim)

    if fim <= inicio:
        fim += timedelta(days=1)

    data_base = inicio.date()
    total_horas = (fim - inicio).total_seconds() / 3600

    # Domingo / Feriado
    if data_base in br_holidays or inicio.weekday() == 6:
        return 0, 0, total_horas

    # Sábado
    if inicio.weekday() == 5:
        return 0, total_horas, 0

    turno = colaborador.turno
    blocos = []
    almoco = None

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

    horas_extras = max(horas_extras, 0)
    horas_extras = min(horas_extras, total_horas - horas_normais)

    return horas_normais, horas_extras, 0


# =====================================================
# FORMATAR HORAS
# =====================================================

def formatar_horas(horas):

    if not horas:
        return "00:00"

    h = int(horas)
    m = int(round((horas - h) * 60))

    return f"{h:02d}:{m:02d}"


# =====================================================
# PROCESSAR RELATORIO
# =====================================================

def processar_relatorio(apontamentos):

    colaboradores = defaultdict(lambda: {
        "matricula": "",
        "nome": "",
        "normais": 0,
        "extra50": 0,
        "extra100": 0
    })

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

    relatorio = []
    totais = {"normais": 0, "extra50": 0, "extra100": 0, "geral": 0}

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

    return relatorio, totais


# =====================================================
# RELATORIO OS
# =====================================================

def relatorio_os(request):

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
    }

    return render(request, "relatorio_os/relatorio_os.html", context)


# =====================================================
# ORCAMENTO
# =====================================================

def proximo_orcamento(request):

    numero = gerar_proximo_orcamento()

    return JsonResponse({"numero": str(numero).zfill(4)})


# =====================================================
# LOG OS
# =====================================================

def log_os(request, numero_os):

    contexto = montar_dados_log_os(numero_os)

    return render(request, "relatorio_os/orcamento_detalhado.html", contexto)


# =====================================================
# PDF LOG OS
# =====================================================
 
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from datetime import datetime, time
from weasyprint import HTML
from django.db.models import Q

from lancamento.models import AberturaOS, ApontamentoHoras

def formatar_horas(horas):
    """Converte horas decimais em string HH:MM"""
    if not horas or horas <= 0:
        return "00:00"
    h = int(horas)
    m = int(round((horas - h) * 60))
    return f"{h:02d}:{m:02d}"

def log_os_pdf(request, numero_os):
    # Buscar OS
    os_obj = get_object_or_404(AberturaOS, numero_os=numero_os)

    # Capturar filtros de data do GET
    data_inicio_str = request.GET.get("data_inicio")
    data_fim_str = request.GET.get("data_fim")
    data_inicio = datetime.strptime(data_inicio_str, "%Y-%m-%d") if data_inicio_str else None
    data_fim = datetime.strptime(data_fim_str, "%Y-%m-%d") if data_fim_str else None

    # Buscar todos os apontamentos da OS
    apontamentos = ApontamentoHoras.objects.filter(ordem_servico=os_obj)

    # Aplicar filtro de intervalo: qualquer apontamento que sobreponha o período
    if data_inicio and data_fim:
        dt_inicio = datetime.combine(data_inicio, time.min)
        dt_fim = datetime.combine(data_fim, time.max)
        apontamentos = apontamentos.filter(Q(data_inicio__lte=dt_fim) & Q(data_fim__gte=dt_inicio))
    elif data_inicio:
        dt_inicio = datetime.combine(data_inicio, time.min)
        apontamentos = apontamentos.filter(data_fim__gte=dt_inicio)
    elif data_fim:
        dt_fim = datetime.combine(data_fim, time.max)
        apontamentos = apontamentos.filter(data_inicio__lte=dt_fim)

    # Agrupar por colaborador
    colab_dict = {}
    total_geral_segundos = 0

    for ap in apontamentos:
        if not ap.data_inicio or not ap.data_fim:
            continue

        duracao_seg = (ap.data_fim - ap.data_inicio).total_seconds()
        if duracao_seg <= 0:
            continue  # ignora apontamentos com duração zero ou negativa

        total_geral_segundos += duracao_seg

        if ap.colaborador.id not in colab_dict:
            colab_dict[ap.colaborador.id] = {
                "colaborador": ap.colaborador,
                "apontamentos": [],
                "total_segundos": 0
            }

        colab_dict[ap.colaborador.id]["apontamentos"].append({
            "data": ap.data_inicio.strftime("%d/%m/%Y"),
            "inicio": ap.data_inicio.strftime("%H:%M"),
            "fim": ap.data_fim.strftime("%H:%M"),
            "duracao": f"{int(duracao_seg//3600):02d}:{int((duracao_seg%3600)//60):02d}",
            "servico": getattr(ap, "servico", "-")
        })
        colab_dict[ap.colaborador.id]["total_segundos"] += duracao_seg

    # Transformar em lista e formatar total por colaborador
    colaboradores = []
    for c in colab_dict.values():
        c["total_horas"] = c["total_segundos"] / 3600
        c["total_fmt"] = formatar_horas(c["total_horas"])
        colaboradores.append(c)

    # Contexto para o template PDF
    context = {
        "logo_path": request.build_absolute_uri('/static/img/logo.png'),
        "data_emissao": datetime.now().strftime("%d/%m/%Y %H:%M"),
        "os": os_obj,
        "colaboradores": colaboradores,
        "total_geral": formatar_horas(total_geral_segundos / 3600)
    }

    # Renderizar HTML
    html_string = render(request, "relatorio_os/orcamento_detalhado.html", context).content.decode("utf-8")

    # Gerar PDF
    pdf = HTML(string=html_string, base_url=request.build_absolute_uri()).write_pdf()

    response = HttpResponse(pdf, content_type="application/pdf")
    response['Content-Disposition'] = f'inline; filename="log_os_{os_obj.numero_os}.pdf"'
    return response
