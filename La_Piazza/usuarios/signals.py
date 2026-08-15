from django.contrib.auth.models import Group
from django.db.models.signals import post_migrate
from django.dispatch import receiver

from .permissions import (
    GRUPO_CLIENTE,
    GRUPO_FUNCIONARIO,
)


@receiver(post_migrate)
def criar_grupos_padrao(sender, **kwargs):
    if sender.name != "usuarios":
        return

    Group.objects.get_or_create(
        name=GRUPO_CLIENTE,
    )

    Group.objects.get_or_create(
        name=GRUPO_FUNCIONARIO,
    )