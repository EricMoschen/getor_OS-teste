from django import forms
from .models import CentroCusto, Cliente

# =====================================================
# Formulário para a Tag Centro de Custos 
# =====================================================

class CentroCustoForm(forms.ModelForm):
    class Meta:
        model = CentroCusto
        fields = ['descricao', 'cod_centro', 'centro_pai']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Exibe apenas os centros "pais" (aqueles que não têm pai)
        self.fields['centro_pai'].queryset = CentroCusto.objects.filter(centro_pai__isnull=True)
        self.fields['centro_pai'].label = "Centro de Custo Pai (opcional)"
        self.fields['centro_pai'].required = False

# =====================================================
# Formulário para cadastro de Clientes
# =====================================================

class ClienteForm (forms.ModelForm):
    class Meta:
        model = Cliente
        fields = ['cod_cliente', 'nome_cliente']
       