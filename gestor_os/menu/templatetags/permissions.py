from django import template

from gestor_os.access import ADMIN_GROUP, user_has_access

register = template.Library()


@register.filter
def has_group(user, group_name):
    return user_has_access(user, {group_name})


@register.filter
def has_any_group(user, group_names):
    if not group_names:
        return False
    names = {name.strip() for name in group_names.split(",") if name.strip()}
    if not names:
        return False
    return user_has_access(user, names | {ADMIN_GROUP})