from django.shortcuts import render, redirect, get_object_or_404
from .models import AberturaOS
from .forms import AberturaOSForm

# --- Abrir / Criar OS ---
def abrir_os(request):
    proximo_numero = AberturaOS.proximo_numero_os()

    if request.method == 'POST':
        form = AberturaOSForm(request.POST)
        if form.is_valid():
            os = form.save(commit=False)
            os.save()
            return redirect('abrir_os')
    else:
        form = AberturaOSForm()  

    ordens = AberturaOS.objects.all().order_by('-data_abertura')

    context = {
        'form': form,
        'proximo_numero': proximo_numero,
        'ordens': ordens
    }
    return render(request, 'abertura_os/abertura_os.html', context)


# --- Editar OS ---
def editar_os(request, pk):
    os = get_object_or_404(AberturaOS, pk=pk)
    if request.method == 'POST':
        form = AberturaOSForm(request.POST, instance=os)
        if form.is_valid():
            form.save()
            return redirect('abrir_os')
    else:
        form = AberturaOSForm(instance=os)

    context = {
        'form': form,
        'editar': True,
        'os': os
    }
    return render(request, 'abertura_os/editar_os.html', context)


# --- Excluir OS ---
def excluir_os(request, pk):
    os = get_object_or_404(AberturaOS, pk=pk)
    if request.method == 'POST':
        os.delete()
        return redirect('abrir_os')
    context = {
        'os': os
    }
    return render(request, 'abertura_os/editar_os.html', context)
