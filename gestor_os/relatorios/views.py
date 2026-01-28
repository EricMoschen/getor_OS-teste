from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from lancamento.models import AberturaOS, ApontamentoHoras 
from datetime import datetime, timedelta, time
from collections import defaultdict
import holidays
from django.db.models import F
from django.utils import timezone



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


def calcular_horas(inicio, fim, colaborador=None):
    inicio = timezone.localtime(inicio)
    fim = timezone.localtime(fim)

    if fim < inicio:
        fim += timedelta(days=1)

    total_horas = (fim - inicio).total_seconds() / 3600

    # Domingo ou feriado = 100%
    if inicio.date() in br_holidays or inicio.weekday() == 6:
        return 0, 0, total_horas

    # Sábado = 50%
    if inicio.weekday() == 5:
        return 0, total_horas, 0

    horas_normais = 0
    horas_50 = 0

    turno = colaborador.turno if colaborador else None
    turnos = []
    horario_almoco = None

    if turno == "A":
        turnos = [(7, 0, 11, 0), (12, 0, 16, 48)]
        horario_almoco = (11, 0, 12, 0)

    elif turno == "B":
        turnos = [(16, 48, 19, 0), (20, 0, 26, 0)]

    elif turno == "HC":
        turnos = [(8, 0, 12, 0), (13, 0, 17, 48)]
        horario_almoco = (12, 0, 13, 0)

    elif turno == "OUTROS" and colaborador.hr_entrada_am:
        turnos = [
            (colaborador.hr_entrada_am.hour, colaborador.hr_entrada_am.minute,
             colaborador.hr_saida_am.hour, colaborador.hr_saida_am.minute),
            (colaborador.hr_entrada_pm.hour, colaborador.hr_entrada_pm.minute,
             colaborador.hr_saida_pm.hour, colaborador.hr_saida_pm.minute),
        ]

        horario_almoco = (
            colaborador.hr_saida_am.hour, colaborador.hr_saida_am.minute,
            colaborador.hr_entrada_pm.hour, colaborador.hr_entrada_pm.minute
        )

    # ===== Calcula horas normais =====
    for h1, m1, h2, m2 in turnos:
        ini_turno = inicio.replace(hour=h1 % 24, minute=m1, second=0)

        fim_turno = inicio.replace(hour=h2 % 24, minute=m2, second=0)
        if h2 >= 24:
            fim_turno += timedelta(days=1)

        ini = max(inicio, ini_turno)
        fim_i = min(fim, fim_turno)

        if ini < fim_i:
            horas_normais += (fim_i - ini).total_seconds() / 3600

    # ===== DESCONTO ALMOÇO =====
    if horario_almoco:
        ah1, am1, ah2, am2 = horario_almoco

        ini_almoco = inicio.replace(hour=ah1, minute=am1, second=0)
        fim_almoco = inicio.replace(hour=ah2, minute=am2, second=0)

        ini = max(inicio, ini_almoco)
        fim_i = min(fim, fim_almoco)

        if ini < fim_i:
            desconto = (fim_i - ini).total_seconds() / 3600
            horas_normais = max(horas_normais - desconto, 0)

    # ===== EXTRAS =====
    horas_50 = max(total_horas - horas_normais, 0)

    return horas_normais, horas_50, 0

def relatorio_os(request):
    os_numero = request.GET.get("os")
    data_inicio = request.GET.get("data_inicio")
    data_fim = request.GET.get("data_fim")

    relatorio = {}
    os_detalhes = None

    apontamentos = ApontamentoHoras.objects.select_related("colaborador", "ordem_servico")

    if os_numero:
        apontamentos = apontamentos.filter(ordem_servico__numero_os=os_numero)

        os_obj = AberturaOS.objects.filter(numero_os=os_numero).first()
        if os_obj:
            os_detalhes = {
                "numero": os_obj.numero_os,
                "descricao": os_obj.descricao_os,
                "cliente": os_obj.cliente,
                "motivo": os_obj.motivo_intervencao
            }

    if data_inicio:
        apontamentos = apontamentos.filter(data_inicio__date__gte=data_inicio)

    if data_fim:
        apontamentos = apontamentos.filter(data_fim__date__lte=data_fim)

    for ap in apontamentos:
        if not ap.data_fim:
            continue

        normais, h50, h100 = calcular_horas(
            ap.data_inicio,
            ap.data_fim,
            ap.colaborador
        )


        mat = ap.colaborador.matricula
        nome = ap.colaborador.nome

        if mat not in relatorio:
            relatorio[mat] = {
                "matricula": mat,
                "nome": nome,
                "horas_normais": 0,
                "horas_50": 0,
                "horas_100": 0,
                "total": 0,
            }

        relatorio[mat]["horas_normais"] += normais
        relatorio[mat]["horas_50"] += h50
        relatorio[mat]["horas_100"] += h100
        relatorio[mat]["total"] += normais + h50 + h100

        # CONVERTE PARA TEXTO AMIGÁVEL
    for mat in relatorio:
        relatorio[mat]["horas_normais_fmt"] = horas_legivel(relatorio[mat]["horas_normais"])
        relatorio[mat]["horas_50_fmt"] = horas_legivel(relatorio[mat]["horas_50"])
        relatorio[mat]["horas_100_fmt"] = horas_legivel(relatorio[mat]["horas_100"])
        relatorio[mat]["total_fmt"] = horas_legivel(relatorio[mat]["total"])

    return render(request, "relatorio_os/relatorio_os.html", {
        "relatorio": list(relatorio.values()),
        "os_detalhes": os_detalhes,
    })



def horas_legivel(horas):
    total_minutos = round(horas * 60)
    h = total_minutos // 60
    m = total_minutos % 60
    return f"{h}h {m:02d}min"
