from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, Http404
from django.contrib.auth.decorators import login_required
from .models import ApontamentoHoras, Colaborador, AberturaOS
from cadastro.models import CentroCusto
from .forms import AberturaOSForm
from django.utils import timezone 
from django.contrib import messages  
from datetime import time, datetime
import holidays

from gestor_os.access import APONTAMENTO_HORAS_GROUP, LANCAMENTO_GROUP, group_required

# Função auxiliar — retorna apenas os centros de custo "pais"
def get_pais_centro_custo():
    return CentroCusto.objects.filter(centro_pai__isnull=True).order_by('descricao')


# --- Abrir / Criar OS ---
@login_required
@group_required(LANCAMENTO_GROUP)
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
@login_required
@group_required(LANCAMENTO_GROUP)
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
@login_required
@group_required(LANCAMENTO_GROUP)
def excluir_os(request, pk):
    os_obj = get_object_or_404(AberturaOS, pk=pk)
    os_obj.delete()
    return redirect('abrir_os')


# --- AJAX para carregar subcentros ---
@login_required
@group_required(LANCAMENTO_GROUP)
def get_subcentros(request):
    pai_id = request.GET.get('pai_id')
    filhos = CentroCusto.objects.filter(centro_pai_id=pai_id).order_by('descricao')
    data = [{"id": f.cod_centro, "descricao": f.descricao} for f in filhos]
    return JsonResponse(data, safe=False)



# --- Folha de Impressão de OS ---
@login_required
@group_required(LANCAMENTO_GROUP)
def imprimir_os(request, pk):
    """
    Exibe a página de impressão da OS selecionada.
    """
    os = get_object_or_404(AberturaOS, pk=pk)

    # Montando o contexto para preencher o template
    context = {
        'os': os,
    }
    return render(request, 'impressao_os/impressao_os.html', context)



# =====================================================
# View: apontar_horas
# =====================================================


BR_HOLIDAYS = holidays.Brazil()  # Para verificar feriados

@login_required
@group_required(LANCAMENTO_GROUP, APONTAMENTO_HORAS_GROUP)
def apontar_horas(request):
    if request.method == "POST":
        matricula = request.POST.get("matricula", "").strip().upper()
        numero_os = request.POST.get("numero_os")
        acao = request.POST.get("acao")

        # Busca colaborador e OS
        colaborador = get_object_or_404(
            Colaborador.objects.only(
                "id", "turno", "hr_entrada_am", "hr_saida_am",
                "hr_entrada_pm", "hr_saida_pm", "matricula", "nome"
            ),
            matricula__iexact=matricula
        )

        os_obj = get_object_or_404(
            AberturaOS.objects.only("id", "numero_os", "situacao"),
            numero_os=numero_os
        )

        if acao == "iniciar" and os_obj.situacao == AberturaOS.STATUS_FINALIZADO:
            messages.error(
                request,
                f"A OS {os_obj.numero_os} está {os_obj.get_situacao_display()} e não permite novos apontamentos, caso seja nescesário o apontamento verifique com o PCM"
            )
            return redirect("apontar_horas")

        agora = timezone.localtime()

        if acao == "iniciar":
            # Verifica OS em aberto
            aberto = ApontamentoHoras.objects.filter(
                colaborador=colaborador,
                data_fim__isnull=True
            ).order_by('-data_inicio').first()

            if aberto:
                try:
                    ApontamentoHoras.encerrar_aberto(colaborador)
                except ValueError as e:
                    messages.error(
                        request,
                        f"Erro! A OS {aberto.ordem_servico.numero_os} está em aberto. {e} "
                        "Verifique com o responsável antes de iniciar uma nova OS."
                    )
                    return redirect("apontar_horas")

            # Classifica tipo de dia
            tipo_dia = ApontamentoHoras.classificar_tipo_dia(agora.date())

            # Cria novo apontamento
            ApontamentoHoras.objects.create(
                colaborador=colaborador,
                ordem_servico=os_obj,
                data_inicio=agora,
                tipo_dia=tipo_dia
            )
            messages.success(request, f"Início da OS {os_obj.numero_os} registrado com sucesso.")

        elif acao == "finalizar":
            aberto = ApontamentoHoras.objects.filter(
                colaborador=colaborador,
                data_fim__isnull=True
            ).order_by('-data_inicio').first()

            if aberto:
                if aberto.data_inicio > agora:
                    messages.error(request, "Erro! Horário de início maior que horário de fim.")
                    return redirect("apontar_horas")
                aberto.data_fim = agora
                aberto.save(update_fields=['data_fim'])
                messages.success(request, f"OS {aberto.ordem_servico.numero_os} finalizada.")
            else:
                messages.warning(request, "Nenhuma OS em andamento para este colaborador.")

        return redirect("apontar_horas")

    # GET → exibir tela
    ordens = AberturaOS.objects.select_related("centro_custo", "cliente").only(
        "numero_os", "descricao_os", "centro_custo__descricao", "cliente__nome_cliente"
    ).order_by("-data_abertura")

    return render(request, "apontar_horas/apontar_horas.html", {"ordens": ordens})


# =============================
# APIs auxiliares
# =============================
@login_required
@group_required(LANCAMENTO_GROUP, APONTAMENTO_HORAS_GROUP)
def api_colaborador(request, matricula):
    try:
        colaborador = Colaborador.objects.get(matricula__iexact=matricula)
        return JsonResponse({
            "id": colaborador.id,
            "matricula": colaborador.matricula,
            "nome": colaborador.nome,
            "funcao": colaborador.funcao,
            "turno": colaborador.turno,
        })
    except Colaborador.DoesNotExist:
        raise Http404("Colaborador não encontrado")

@login_required
@group_required(LANCAMENTO_GROUP, APONTAMENTO_HORAS_GROUP)
def api_os(request, numero):
    try:
        os_obj = AberturaOS.objects.get(numero_os__iexact=numero)
        return JsonResponse({
            "id": os_obj.id,
            "numero_os": os_obj.numero_os,
            "descricao": os_obj.descricao_os,
        })
    except AberturaOS.DoesNotExist:
         raise Http404("OS não encontrada")

@login_required
@group_required(LANCAMENTO_GROUP, APONTAMENTO_HORAS_GROUP)      
def api_os_detalhes(request, pk):
    os_obj = get_object_or_404(
        AberturaOS.objects.select_related("centro_custo", "cliente", "motivo_intervencao"),
        pk=pk,
    )
    return JsonResponse({
        "id": os_obj.id,
        "numero_os": os_obj.numero_os,
        "descricao_os": os_obj.descricao_os,
        "centro_custo": {
            "id": os_obj.centro_custo.pk if os_obj.centro_custo else None,
            "label": os_obj.centro_custo.descricao if os_obj.centro_custo else "",
        },
        "cliente": os_obj.cliente.pk if os_obj.cliente else None,
        "motivo_intervencao": os_obj.motivo_intervencao.pk if os_obj.motivo_intervencao else None,
        "ssm": os_obj.ssm,
        "situacao": os_obj.situacao,
    })

