from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from lancamento.models import AberturaOS  # Certifique-se que é deste app


# =====================================================
# Finalizar OS
# =====================================================
def finalizar_os(request):
    ordens = AberturaOS.objects.all().order_by("-numero_os")

    if request.method == "POST":
        numero_os = request.POST.get("numero_os_hidden")
        observacoes = request.POST.get("observacoes", "").strip()

        # Verifica se a observação foi informada
        if not observacoes:
            return render(request, "finalizar_os/finalizar_os.html", {
                "ordens": ordens,
                "erro": "Informe a observação antes de finalizar a OS."
            })

        try:
            os = AberturaOS.objects.get(numero_os=numero_os)
            os.observacoes = observacoes  # Salva a observação diretamente na OS
            os.situacao = "FI"            # Marca como finalizada
            os.save()

            return redirect("finalizar_os")

        except AberturaOS.DoesNotExist:
            return render(request, "finalizar_os/finalizar_os.html", {
                "ordens": ordens,
                "erro": "OS não encontrada."
            })

    # GET → renderiza tela normalmente
    return render(request, "finalizar_os/finalizar_os.html", {
        "ordens": ordens
    })


# =====================================================
# Buscar OS via AJAX
# =====================================================
def buscar_os(request, numero_os):
    try:
        os = AberturaOS.objects.get(numero_os=numero_os)
        return JsonResponse({
            "descricao": os.descricao_os,
            "situacao": os.get_situacao_display(),
            "observacoes": os.observacoes or ""
        })
    except AberturaOS.DoesNotExist:
        return JsonResponse({"erro": True})
