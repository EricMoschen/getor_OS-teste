from django.db import models
from django.utils import timezone
from cadastro.models import CentroCusto, Cliente, Intervencao

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
