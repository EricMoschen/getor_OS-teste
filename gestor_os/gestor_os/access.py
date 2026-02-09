from functools import wraps

from django.core.exceptions import PermissionDenied

ADMIN_GROUP = "Administrador"
CADASTRO_GROUP = "Cadastro"
LANCAMENTO_GROUP = "Lancamento"
APONTAMENTO_HORAS_GROUP = "ApontamentoHoras"
RELATORIOS_GROUP = "Relatorios"

ALL_GROUPS = (
    ADMIN_GROUP,
    CADASTRO_GROUP,
    LANCAMENTO_GROUP,
    APONTAMENTO_HORAS_GROUP,
    RELATORIOS_GROUP,
)


def user_has_access(user, group_names):
    if not user or not user.is_authenticated:
        return False
    if user.is_superuser:
        return True
    return user.groups.filter(name__in=group_names).exists()


def group_required(*group_names):
    required_groups = set(group_names) | {ADMIN_GROUP}

    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                raise PermissionDenied
            if user_has_access(request.user, required_groups):
                return view_func(request, *args, **kwargs)
            raise PermissionDenied

        return _wrapped_view

    return decorator