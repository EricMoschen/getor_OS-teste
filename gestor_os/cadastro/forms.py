from django import forms
from .models import CentroCusto, Cliente, Intervencao, Colaborador

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
        fields = '__all__'
       
       
# =====================================================
# Formulário para cadastro de Clientes
# =====================================================

class IntervencaoForm(forms.ModelForm):
    class Meta:
        model = Intervencao
        fields = '__all__'
        
        
# =====================================================
# Formulário para cadastro de Colaboradores
# =====================================================

class ColaboradorForm(forms.ModelForm):
    class Meta:
        model = Colaborador
        fields = [
            'matricula', 'nome', 'funcao', 'valor_hora', 'turno',
            'hr_entrada_am', 'hr_saida_am', 'hr_entrada_pm', 'hr_saida_pm'
        ]
        widgets = {
            'matricula': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: 1234'
            }),
            'nome': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nome completo do colaborador'
            }),
            'funcao': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Função ou cargo'
            }),
            'valor_hora': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'placeholder': 'Ex: 12.50'
            }),
            'turno': forms.Select(attrs={'class': 'form-select', 'id': 'id_turno'}),
            'hr_entrada_am': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'hr_saida_am': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'hr_entrada_pm': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'hr_saida_pm': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
        }

    def clean(self):
        cleaned_data = super(). clean()
        turno = cleaned_data.get('turno')
        
         # Se o turno for OUTROS, exige que os horários personalizados sejam preenchidos
        if turno == 'OUTROS':
            required_fields = ['hr_entrada_am', 'hr_saida_am', 'hr_entrada_pm', 'hr_saida_pm']
            for field in required_fields:
                if not cleaned_data.get(field):
                    self.add_error(field, 'Campo obrigatório para o turno OUTROS.')
        return cleaned_data
        