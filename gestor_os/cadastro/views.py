from django.shortcuts import render, redirect
from .forms import CentroCustoForm, ClienteForm
from .models import CentroCusto, Cliente




# =====================================================
# Cadastro de Centro de Custos
# =====================================================

def montar_hierarquia(centros):
    resultado = []
    for centro in centros:
        filhos = montar_hierarquia(centro.subcentros.all())
        resultado.append({'centro': centro, 'filhos': filhos})
    return resultado

def cadastrar_centro_custo(request):
    if request.method == 'POST':
        form = CentroCustoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('cadastrar_centro_custo')
    else:
        form = CentroCustoForm()

    centros_pai = CentroCusto.objects.filter(centro_pai__isnull=True).prefetch_related('subcentros')
    hierarquia = montar_hierarquia(centros_pai)

    return render(request, 'cadastro_centro/cadastro_centro_custo.html', {
        'form': form,
        'hierarquia': hierarquia
    })



# =====================================================
# Cadastro de Clientes
# =====================================================


def cadastro_cliente(request):
    if request.method == 'POST':
        cod = request.POST.get('cod_cliente')
        nome = request.POST.get('nome_cliente')
        if cod and nome:
            Cliente.objects.create(cod_cliente=cod, nome_cliente=nome)
        return redirect('cadastro_cliente')
    clientes = Cliente.objects.all()
    return render(request, 'cadastro_cliente/cadastro_cliente.html', {'clientes': clientes})