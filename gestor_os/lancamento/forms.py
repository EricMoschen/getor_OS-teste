from django import forms
from .models import AberturaOS, Cliente

class AberturaOSForm(forms.ModelForm):
    class Meta:
        model = AberturaOS
        exclude = ['numero_os', 'data_abertura', 'centro_custo','situacao']
        fields = [
            'descricao_os',
            'cliente',
            'motivo_intervencao',
            'ssm'
        ]
        widgets = {
            'descricao_os': forms.Textarea(attrs={'class':'w-full p-2 border rounded', 'rows':3}),
            'motivo_intervencao': forms.Select(attrs={'class':'w-full p-2 border rounded'}),
            'ssm': forms.TextInput(attrs={'class':'w-full p-2 border rounded'}),
            'situacao': forms.Select(attrs={'class':'w-full p-2 border rounded'}),
        }

    cliente = forms.ModelChoiceField(
        queryset=Cliente.objects.all(),
        required=False,
        empty_label="Selecione um cliente",
        widget=forms.Select(attrs={
            'class': 'w-full p-2 border rounded'
        })
)
