from django.db import models
from datetime import time


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
        return f"{self.cod_intervencao} - {self.descricao}"
    
    
# =====================================================
# Model para Cadastro do Colaborador
# =====================================================
class Colaborador(models.Model):
    
    TURNO_OPCOES = [
        ('A', 'A - 07:00 às 11:00 / 12:00 às 16:48'),
        ('B', 'B - 16:48 às 19:00 / 20:00 às 02:00'),
        ('HC', 'H/C - 08:00 às 12:00 / 13:00 às 17:48'),
        ('OUTROS', 'Outros'),
    ]
    
    matricula = models.CharField(max_length=4, unique=True, verbose_name='Número da Matrícula')
    nome = models.CharField(max_length=255, verbose_name='Nome do Colaborador')
    funcao = models.CharField(max_length=150, verbose_name='Função')
    valor_hora = models.DecimalField(max_digits=7, decimal_places=2, default=0.00, verbose_name='Valor da Hora (R$)')
    turno = models.CharField(max_length=10, choices=TURNO_OPCOES, verbose_name='Turno')
    
    
    # Campos para horários personalizados (quando turno for OUTROS)
    hr_entrada_am = models.TimeField(blank=True, null=True, verbose_name='Entrada (Manhã)')
    hr_saida_am = models.TimeField(blank=True, null=True, verbose_name='Saída (Manhã)')
    hr_entrada_pm = models.TimeField(blank=True, null=True, verbose_name='Entrada (Tarde)')
    hr_saida_pm = models.TimeField(blank=True, null=True, verbose_name='Saída (Tarde)')
    
    def __str__(self):
        return f"{self.matricula} - {self.nome}"
    
    class Meta:
        verbose_name = "Colaborador"
        verbose_name_plural = "Colaboradores"
        ordering = ['nome']

    # =====================================================
    # Métodos para calcular horários do turno
    # =====================================================
    def calcular_horario_inicio_turno(self):
        turno = self.turno
        if turno == 'A':
            return time(7, 0)
        elif turno == 'B':
            return time(16, 48)
        elif turno == 'HC':
            return time(8, 0)
        elif turno == 'OUTROS':
            return self.hr_entrada_am or time(7, 0)
        return time(7, 0)

    def calcular_horario_fim_turno(self):
        turno = self.turno
        if turno == 'A':
            return time(16, 48)
        elif turno == 'B':
            return time(2, 0)
        elif turno == 'HC':
            return time(17, 48)
        elif turno == 'OUTROS':
            return self.hr_saida_pm or time(17, 48)
        return time(17, 48)