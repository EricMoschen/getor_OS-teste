from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.utils import timezone

from .models import AberturaOS, ApontamentoHoras


@receiver(pre_save, sender=AberturaOS)
def fechar_apontamentos_os_finalizada(sender, instance, **kwargs):

    # Se for criação, não faz nada
    if not instance.pk:
        return

    try:
        os_antiga = AberturaOS.objects.get(pk=instance.pk)
    except AberturaOS.DoesNotExist:
        return

    # Verifica se mudou para FINALIZADA
    if (
        os_antiga.situacao != AberturaOS.STATUS_FINALIZADO
        and instance.situacao == AberturaOS.STATUS_FINALIZADO
    ):

        agora = timezone.localtime()

        apontamentos_abertos = ApontamentoHoras.objects.filter(
            ordem_servico=instance,
            data_fim__isnull=True
        )

        for apontamento in apontamentos_abertos:
            apontamento.data_fim = agora
            apontamento.tipo_dia = ApontamentoHoras.classificar_tipo_dia(agora.date())
            apontamento.save(update_fields=["data_fim", "tipo_dia"])
