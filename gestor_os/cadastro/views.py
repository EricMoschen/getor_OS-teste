from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .forms import CentroCustoForm, ClienteForm, IntervencaoForm, ColaboradorForm
from .models import CentroCusto, Cliente, Intervencao, Colaborador
from django.db.models import Q


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

    mensagem_erro = None
    

    if request.method == 'POST':
        cliente_id = request.POST.get("cliente_id") or None
        cod = request.POST.get("cod_cliente")
        nome = request.POST.get("nome_cliente")

        # VERIFICACR SE O CÓDIGO JÁ EXISTE EM OUTRO CLIENTE
        cliente_existente = Cliente.objects.filter(cod_cliente=cod).exclude(pk=cliente_id).first()

        if Cliente.objects.filter(cod_cliente=cod).exclude(pk=cliente_id).exists():
            mensagem_erro = f"Já existe um Cliente com o Código Informado: <br> {cod} - {cliente_existente.nome_cliente}."
        else:
        # EDITAR CLIENTE
            if cliente_id:
                cliente = Cliente.objects.get(pk=cliente_id)
                cliente.cod_cliente = cod 
                cliente.nome_cliente = nome
                cliente.save()

            # CADASTRAR NOVO CLIENTE
            else:
                Cliente.objects.create(
                    cod_cliente=cod,
                    nome_cliente=nome
                )

            return redirect('cadastro_cliente')

    # LISTAR CLIENTES
    clientes = Cliente.objects.all().order_by('cod_cliente')
    return render(request, "cadastro_cliente/cadastro_cliente.html", {"clientes": clientes, "mensagem_erro":mensagem_erro})


def excluir_cliente(request, pk):
    cliente = get_object_or_404(Cliente, pk=pk)

    if request.method == 'POST':
        cliente.delete()
        return redirect('cadastro_cliente')

    # opcional: retornar erro ou redirect
    return redirect('cadastro_cliente')


# =====================================================
# Cadastro de Intervenções
# =====================================================
def cadastro_intervencao(request):
    if request.method == 'POST':
        interv_id = request.POST.get('intervencao_id')
        descricao = request.POST.get('descricao')

        if descricao:
            if interv_id:  # Editar
                interv = get_object_or_404(Intervencao, cod_intervencao=interv_id)
                interv.descricao = descricao
                interv.save()
            else:  # Criar
                # Gera o próximo código automático
                prox_cod = (Intervencao.objects.aggregate(max_cod=models.Max('cod_intervencao'))['max_cod'] or 0) + 1
                Intervencao.objects.create(cod_intervencao=prox_cod, descricao=descricao)

        return redirect('cadastro_intervencao')

    intervencoes = Intervencao.objects.all().order_by('cod_intervencao')
    return render(request, 'cadastro_intervencao/cadastro_intervencao.html', {
        'intervencoes': intervencoes
    })

def excluir_intervencao(request, pk):
    interv = get_object_or_404(Intervencao, pk=pk)
    interv.delete()
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

def editar_colaborador(request, pk):
    colaborador = get_object_or_404(Colaborador, pk=pk)

    if request.method == 'POST':
        form = ColaboradorForm(request.POST, instance=colaborador)
        if form.is_valid():
            form.save()
            messages.success(request, f'Colaborador {colaborador.nome} atualizado com sucesso!')
            return redirect('cadastro_colaborador')
        else:
            messages.error(request, 'Erro ao atualizar o colaborador. Verifique os campos.')
    else:
        form = ColaboradorForm(instance=colaborador)

    colaboradores = Colaborador.objects.all().order_by('nome')

    context = {
        'form': form,
        'colaboradores': colaboradores,
        'editando': True,
        'colaborador_editando': colaborador
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