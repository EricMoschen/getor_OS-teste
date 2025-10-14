from django import forms
from .models import AberturaOS


# =====================================================
# Formulário de Abertura de Ordens de Serviço
# =====================================================
class AberturaOSForm(forms.ModelForm):
    class Meta:
        model = AberturaOS
        fields = [
            'descricao_os',
            'centro_custo',
            'cliente',
            'motivo_intervencao',
            'ssm',
            'situacao',
        ]
        widgets = {
            'descricao_os': forms.Textarea(attrs={
                'class': 'w-full p-2 border rounded',
                'rows': 3,
                'placeholder': 'Descreva brevemente o serviço a ser realizado...'
            }),
            'centro_custo': forms.Select(attrs={'class': 'w-full p-2 border rounded'}),
            'cliente': forms.Select(attrs={'class': 'w-full p-2 border rounded'}),
            'motivo_intervencao': forms.Select(attrs={'class': 'w-full p-2 border rounded'}),
            'ssm': forms.TextInput(attrs={
                'class': 'w-full p-2 border rounded',
                'placeholder': 'Informe o número da SSM'
            }),
            'situacao': forms.Select(attrs={'class': 'w-full p-2 border rounded'}),
        }
