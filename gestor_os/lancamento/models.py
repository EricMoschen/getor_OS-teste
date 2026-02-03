from django.db import models
from django.utils import timezone
from cadastro.models import CentroCusto, Cliente, Intervencao, Colaborador
from datetime import datetime, time, timedelta
import holidays


# =====================================================
# Model para Abertura de Ordens de Serviço
# =====================================================
class AberturaOS(models.Model):

    STATUS_ABERTO = "AB"
    STATUS_FINALIZADO = "FI"

    STATUS_OPCOES = [
        (STATUS_ABERTO, "Em Aberto"),
        (STATUS_FINALIZADO, "Finalizado"),
    ]

    numero_os = models.CharField(max_length=8, unique=True, editable=False)
    descricao_os = models.TextField()
    centro_custo = models.ForeignKey(CentroCusto, on_delete=models.PROTECT)
    cliente = models.ForeignKey(Cliente, on_delete=models.PROTECT,null=True, blank= True)
    motivo_intervencao = models.ForeignKey(Intervencao, on_delete=models.PROTECT,related_name='aberturaos')
    ssm = models.CharField(max_length=10)
    situacao = models.CharField(
        max_length=2,
        choices=STATUS_OPCOES,
        default='AB',
        verbose_name='Situação da OS'
    )
    data_abertura = models.DateTimeField(auto_now_add=True)

    
    observacoes = models.TextField(blank=True, null=True)

    @classmethod
    def proximo_numero_os(cls):
        """Calcula o próximo número de OS sem salvar."""
        ano_atual = timezone.now().year % 100  # Exemplo: 2025 -> 25
        ultimo = (
            cls.objects.filter(numero_os__endswith=f"-{ano_atual}")
            .order_by("-numero_os")
            .first()
        )

        if ultimo:
            sequencial = int(ultimo.numero_os.split("-")[0]) + 1
        else:
            sequencial = 1

        return f"{sequencial:03d}-{ano_atual}"

    def save(self, *args, **kwargs):
        """Gera automaticamente o número da OS antes de salvar."""
        if not self.numero_os:
            self.numero_os = self.proximo_numero_os()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"OS {self.numero_os} - {self.descricao_os[:30]}"


# =====================================================
# Model: Apontamento de Horas
# =====================================================


BR_HOLIDAYS = holidays.Brazil()

class ApontamentoHoras(models.Model):
    colaborador = models.ForeignKey('cadastro.Colaborador', on_delete=models.PROTECT)
    ordem_servico = models.ForeignKey('AberturaOS', on_delete=models.PROTECT)

    data_inicio = models.DateTimeField(default=timezone.now)
    data_fim = models.DateTimeField(blank=True, null=True)
    tipo_dia = models.CharField(max_length=20, blank=True)

    def __str__(self):
        return f"{self.colaborador.nome} - {self.ordem_servico.numero_os}"

    # =====================================================
    # RETORNA INTERVALOS NORMAIS DO TURNO
    # =====================================================
    def obter_intervalos_turno(self):
        turno = self.colaborador.turno

        if turno == "A":
            return [(time(7, 0), time(11, 0)), (time(12, 0), time(16, 48))]

        elif turno == "B":
            return [(time(16, 48), time(19, 0)), (time(20, 0), time(2, 0))]

        elif turno == "HC":
            return [(time(8, 0), time(12, 0)), (time(13, 0), time(17, 48))]

        elif turno == "OUTROS":
            return [
                (self.colaborador.hr_entrada_am, self.colaborador.hr_saida_am),
                (self.colaborador.hr_entrada_pm, self.colaborador.hr_saida_pm),
            ]

        return []

    # =====================================================
    # CLASSIFICA O DIA
    # =====================================================
    @staticmethod
    def classificar_tipo_dia(data):
        if data in BR_HOLIDAYS or data.weekday() == 6:
            return "Dom/Feriado"
        elif data.weekday() == 5:
            return "Sábado"
        return "Dia Normal"

    # =====================================================
    # CALCULA HORAS NORMAIS vs EXTRA
    # =====================================================
    def calcular_horas(self):
        if not self.data_fim:
            return 0, 0, 0

        inicio = timezone.localtime(self.data_inicio)
        fim = timezone.localtime(self.data_fim)

        total_horas = (fim - inicio).total_seconds() / 3600
        tipo_dia = self.classificar_tipo_dia(inicio.date())

        horas_normais = 0
        horas_50 = 0
        horas_100 = 0

        # Domingo / Feriado
        if tipo_dia == "Dom/Feriado":
            return 0, 0, total_horas

        # Sábado
        if tipo_dia == "Sábado":
            return 0, total_horas, 0

        # Dia normal → comparar com turno
        for entrada, saida in self.obter_intervalos_turno():
            if not entrada or not saida:
                continue

            ini_turno = datetime.combine(inicio.date(), entrada)
            fim_turno = datetime.combine(inicio.date(), saida)

            # Turno que passa da meia noite
            if saida < entrada:
                fim_turno = fim_turno + timedelta(days=1)

            ini_turno = timezone.make_aware(ini_turno)
            fim_turno = timezone.make_aware(fim_turno)

            inter_inicio = max(inicio, ini_turno)
            inter_fim = min(fim, fim_turno)

            if inter_inicio < inter_fim:
                horas_normais += (inter_fim - inter_inicio).total_seconds() / 3600

        horas_50 = max(total_horas - horas_normais, 0)

        return horas_normais, horas_50, horas_100
    

    # =====================================================
    # MÉTODO PARA ENCERRAR OS ABERTA
    # =====================================================

    @classmethod
    def encerrar_aberto(cls, colaborador):
        aberto = cls.objects.filter(
            colaborador=colaborador,
            data_fim__isnull=True
        ).order_by('-data_inicio').first()

        if not aberto:
            raise ValueError("Nenhum apontamento aberto encontrado.")

        agora = timezone.localtime()

        if aberto.data_inicio > agora:
            raise ValueError("Horário de início maior que horário atual.")

        aberto.data_fim = agora
        aberto.save(update_fields=["data_fim"])

        return aberto