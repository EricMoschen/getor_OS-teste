from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from .models import AberturaOS
from cadastro.models import CentroCusto
from .forms import AberturaOSForm

# Função auxiliar — retorna apenas os centros de custo "pais"
def get_pais_centro_custo():
    return CentroCusto.objects.filter(centro_pai__isnull=True).order_by('descricao')


# --- Abrir / Criar OS ---
def abrir_os(request):
    proximo_numero = AberturaOS.proximo_numero_os()

    if request.method == 'POST':
        form = AberturaOSForm(request.POST)
        if form.is_valid():
            os_obj = form.save(commit=False)
            os_obj.numero_os = proximo_numero
            os_obj.situacao = 'AB'

            centro_id = request.POST.get('centro_custo')
            if centro_id:
                try:
                    os_obj.centro_custo = CentroCusto.objects.get(pk=centro_id)
                except CentroCusto.DoesNotExist:
                    form.add_error(None, "Centro de custo selecionado não existe.")
            else:
                form.add_error(None, "Selecione um centro de custo (pai ou filho).")

            if not form.errors:
                os_obj.save()
                return redirect('abrir_os')
    else:
        form = AberturaOSForm()

    pais_centro_custo = get_pais_centro_custo()
    ordens = AberturaOS.objects.all().order_by('-data_abertura')

    context = {
        'form': form,
        'proximo_numero': proximo_numero,
        'ordens': ordens,
        'pais_centro_custo': pais_centro_custo,
        'modo_edicao': False,
    }
    return render(request, 'abertura_os/abertura_os.html', context)


# --- Editar OS ---
def editar_os(request, pk):
    os_instance = get_object_or_404(AberturaOS, pk=pk)

    if request.method == 'POST':
        form = AberturaOSForm(request.POST, instance=os_instance)
        if form.is_valid():
            form.save()
            return redirect('abrir_os')
    else:
        form = AberturaOSForm(instance=os_instance)

    ordens = AberturaOS.objects.all().order_by('-data_abertura')
    pais_centro_custo = get_pais_centro_custo()

    return render(request, 'abertura_os/abertura_os.html', {
        'form': form,
        'proximo_numero': os_instance.numero_os,
        'ordens': ordens,
        'pais_centro_custo': pais_centro_custo,
        'modo_edicao': True,
        'os_id': os_instance.id,
        'selected_centro_label': os_instance.centro_custo.descricao if os_instance.centro_custo else '',
    })


# --- Excluir OS ---
def excluir_os(request, pk):
    os_obj = get_object_or_404(AberturaOS, pk=pk)
    os_obj.delete()
    return redirect('abrir_os')


# --- AJAX para carregar subcentros ---
def get_subcentros(request):
    pai_id = request.GET.get('pai_id')
    filhos = CentroCusto.objects.filter(centro_pai_id=pai_id).order_by('descricao')
    data = [{"id": f.cod_centro, "descricao": f.descricao} for f in filhos]
    return JsonResponse(data, safe=False)



# --- Folha de Impressão de OS ---
def imprimir_os (request):
    return render (request, 'impressao_os/impressao.html')