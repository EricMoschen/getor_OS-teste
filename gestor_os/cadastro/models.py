from django.db import models


# =====================================================
# Centro de Custos Tag 
# =====================================================

class CentroCusto(models.Model):
    descricao = models.CharField(max_length=100)
    cod_centro = models.IntegerField(primary_key=True)
    centro_pai = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name='subcentros'
    )

    def __str__(self):
        if self.centro_pai:
            return f"{self.centro_pai.descricao} -> {self.descricao}"
        return self.descricao