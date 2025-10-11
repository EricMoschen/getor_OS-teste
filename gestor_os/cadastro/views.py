from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .forms import CentroCustoForm, ClienteForm, IntervencaoForm, ColaboradorForm
from .models import CentroCusto, Cliente, Intervencao, Colaborador


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
            # Criar cliente usando o código informado pelo usuário
            Cliente.objects.create(pk=cod, nome_cliente=nome)
            return redirect('cadastro_cliente')

    clientes = Cliente.objects.all()
    return render(request, 'cadastro_cliente/cadastro_cliente.html', {'clientes': clientes})

def excluir_cliente(request, pk):
    cliente = get_object_or_404(Cliente, pk=pk)
    if request.method == 'POST':
        cliente.delete()
        return redirect('cadastro_cliente')

# =====================================================
# Cadastro de Intervenções
# =====================================================
def cadastro_intervencao(request):
    if request.method == 'POST':
        descricao = request.POST.get('descricao')
        if descricao:
            Intervencao.objects.create(descricao=descricao)
            return redirect('cadastro_intervencao')

    intervencoes = Intervencao.objects.all()
    return render(request, 'cadastro_intervencao/cadastro_intervencao.html', {
        'intervencoes': intervencoes
    })

def excluir_intervencao(request, pk):
    intervencao = get_object_or_404(Intervencao, pk=pk)
    intervencao.delete()
    return redirect('cadastro_intervencao')

# =====================================================
# Cadastro de Colaboradores
# =====================================================

def cadastro_colaborador(request):
    # Formulário
    if request.method == 'POST':
        form = ColaboradorForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Colaborador cadastrado com sucesso!')
            return redirect('cadastro_colaborador')
        else:
            messages.error(request, 'Erro ao cadastrar o colaborador. Verifique os campos.')
    else:
        form = ColaboradorForm()

    # Listagem de colaboradores
    colaboradores = Colaborador.objects.all().order_by('nome')

    context = {
        'form': form,
        'colaboradores': colaboradores,
    }
    return render(request, 'cadastro_colaborador/cadastro_colaborador.html', context)


def excluir_colaborador(request, pk):
    colaborador = get_object_or_404(Colaborador, pk=pk)

    if request.method == 'POST':
        colaborador.delete()
        messages.success(request, f'Colaborador {colaborador.nome} excluído com sucesso!')
        return redirect('cadastro_colaborador')

    # Caso alguém tente acessar via GET, redireciona
    return redirect('cadastro_colaborador')