from django.shortcuts import render, redirect
from .forms import CentroCustoForm



# =====================================================
# Cadastro de Centro de Custos
# =====================================================

def cadastrar_centro_custo(request):
    if request.method == 'POST':
        form = CentroCustoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('cadastrar_centro_custo')
    else:
        form = CentroCustoForm()

    # Mostra a lista hierárquica de centros já cadastrados
    centros_pai = form.fields['centro_pai'].queryset.prefetch_related('subcentros')
    return render(request, 'cadastro_centro_custo.html', {'form': form, 'centros_pai': centros_pai})

