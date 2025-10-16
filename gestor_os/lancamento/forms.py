from django import forms
from .models import AberturaOS

class AberturaOSForm(forms.ModelForm):
    class Meta:
        model = AberturaOS
        # exclui campos gerados automaticamente e o fk centro_custo (preenchido na view)
        exclude = ['numero_os', 'situacao', 'data_abertura', 'centro_custo']
        widgets = {
            'descricao_os': forms.Textarea(attrs={'class':'w-full p-2 border rounded', 'rows':3}),
            'cliente': forms.Select(attrs={'class':'w-full p-2 border rounded'}),
            'motivo_intervencao': forms.Select(attrs={'class':'w-full p-2 border rounded'}),
            'ssm': forms.TextInput(attrs={'class':'w-full p-2 border rounded'}),
        }
