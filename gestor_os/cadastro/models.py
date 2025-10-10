from django.db import models


# =====================================================
# Model para Centro de Custos e Tag 
# =====================================================

class CentroCusto(models.Model):
    cod_centro = models.IntegerField(primary_key=True)
    descricao = models.CharField(max_length=100)
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
    
    

# =====================================================
# Model para Cadastro de Clientes
# =====================================================

class Cliente(models.Model):
    
    cod_cliente = models.IntegerField(primary_key= True)
    nome_cliente = models.CharField(max_length= 100)
    
    def __str__(self):
        return f"{self.cod_cliente} - {self.nome_cliente}"
    
    
# =====================================================
# Model para Intervenção
# =====================================================

class Intervencao(models.Model):
    cod_intervencao = models.IntegerField(primary_key=True)
    descricao = models.CharField(max_length=200)

    def __str__(self):
        return f"{self.cod_intevencao} - {self.descricao}"