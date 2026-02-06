import os
from django.conf import settings

SEQ_PATH = os.path.join(settings.BASE_DIR, "controle_orcamento.txt")


def ler_numero_orcamento():
    """
    Apenas lê o número atual (não incrementa)
    """

    if not os.path.exists(SEQ_PATH):
        with open(SEQ_PATH, "w") as f:
            f.write("1")

    with open(SEQ_PATH, "r") as f:
        numero = int(f.read().strip())

    return numero


def gerar_proximo_orcamento():
    """
    Lê e incrementa
    """

    numero = ler_numero_orcamento()

    with open(SEQ_PATH, "w") as f:
        f.write(str(numero + 1))

    return numero






from datetime import timedelta

def calcular_duracao(inicio, fim):
    if not fim:
        return timedelta()

    return fim - inicio


def formatar_duracao(td):
    total_segundos = int(td.total_seconds())

    horas = total_segundos // 3600
    minutos = (total_segundos % 3600) // 60

    return f"{horas}h{minutos:02d}"




from datetime import time


def calcular_horas(inicio, fim, colaborador=None):

    duracao = fim - inicio
    horas = duracao.total_seconds() / 3600

    # EXEMPLO SIMPLES
    # (Você pode evoluir depois com feriado, noturno etc)

    normais = horas
    h50 = 0
    h100 = 0

    return normais, h50, h100



# relatorios/utils.py
from lancamento.models import ApontamentoHoras, AberturaOS

def montar_dados_log_os(os_obj, data_inicio=None, data_fim=None):
    # Filtra os apontamentos pelo intervalo de datas
    apontamentos = ApontamentoHoras.objects.filter(ordem_servico=os_obj)
    if data_inicio:
        apontamentos = apontamentos.filter(data_inicio__gte=data_inicio)
    if data_fim:
        apontamentos = apontamentos.filter(data_fim__lte=data_fim)

    dados = []
    total_segundos = 0

    for ap in apontamentos:
        inicio = ap.data_inicio
        fim = ap.data_fim
        if fim and inicio:
            duracao = fim - inicio
            total_segundos += duracao.total_seconds()
            horas = duracao.seconds // 3600
            minutos = (duracao.seconds % 3600) // 60
            dados.append({
                'colaborador': ap.colaborador.nome,
                'inicio': inicio.strftime("%d/%m/%Y %H:%M"),
                'fim': fim.strftime("%d/%m/%Y %H:%M"),
                'duracao': f"{horas:02d}:{minutos:02d}"
            })

    total_horas = int(total_segundos // 3600)
    total_minutos = int((total_segundos % 3600) // 60)
    return dados, f"{total_horas:02d}:{total_minutos:02d}"

