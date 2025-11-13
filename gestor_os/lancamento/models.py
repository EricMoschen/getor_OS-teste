from django.db import models
from django.utils import timezone
from cadastro.models import CentroCusto, Cliente, Intervencao, Colaborador
from datetime import datetime, time, timedelta

# =====================================================
# Model para Abertura de Ordens de Serviço
# =====================================================
class AberturaOS(models.Model):
    STATUS_OPCOES = [
        ('AB', 'Em Aberto'),
        ('FI', 'Finalizado'),
    ]

    numero_os = models.CharField(max_length=8, unique=True, editable=False)
    descricao_os = models.TextField()
    centro_custo = models.ForeignKey(CentroCusto, on_delete=models.PROTECT)
    cliente = models.ForeignKey(Cliente, on_delete=models.PROTECT)
    motivo_intervencao = models.ForeignKey(Intervencao, on_delete=models.PROTECT)
    ssm = models.CharField(max_length=10)
    situacao = models.CharField(
        max_length=2,
        choices=STATUS_OPCOES,
        default='AB',
        verbose_name='Situação da OS'
    )
    data_abertura = models.DateTimeField(auto_now_add=True)

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

class ApontamentoHoras(models.Model):
    colaborador = models.ForeignKey('cadastro.Colaborador', on_delete=models.PROTECT, related_name='apontamentos')
    ordem_servico = models.ForeignKey('AberturaOS', on_delete=models.PROTECT, related_name='apontamentos')
    data_inicio = models.DateTimeField(default=timezone.now)
    data_fim = models.DateTimeField(blank=True, null=True)

    class Meta:
        verbose_name = "Apontamento de Horas"
        verbose_name_plural = "Apontamentos de Horas"
        ordering = ['-data_inicio']

    def __str__(self):
        return f"{self.colaborador.nome} - {self.ordem_servico.numero_os}"

    # =====================================================
    # Função auxiliar para obter o fim do turno
    # =====================================================
    def calcular_horario_fim_turno(self):
        turno = self.colaborador.turno

        if turno == 'A':
            return time(16, 48)
        elif turno == 'B':
            return time(2, 0)
        elif turno == 'HC':
            return time(17, 48)
        elif turno == 'OUTROS':
            # Usa o horário personalizado, se houver
            return self.colaborador.hr_saida_pm or time(17, 48)
        return time(17, 48)

    # =====================================================
    # Método para finalizar automaticamente a OS anterior
    # =====================================================
    @classmethod
    def encerrar_aberto(cls, colaborador):
        aberto = cls.objects.filter(colaborador=colaborador, data_fim__isnull=True).order_by('-data_inicio').first()
        if not aberto:
            return

        agora = timezone.now()
        # Se for outro dia, finaliza no horário do turno
        if aberto.data_inicio.date() != agora.date():
            fim_turno = aberto.calcular_horario_fim_turno()
            fim_completo = datetime.combine(aberto.data_inicio.date(), fim_turno)
            aberto.data_fim = timezone.make_aware(fim_completo)
        else:
            aberto.data_fim = agora

        aberto.save(update_fields=['data_fim'])
        return aberto
