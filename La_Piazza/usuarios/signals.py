from django.contrib.auth.models import Group, Permission
from django.db.models.signals import post_migrate
from django.dispatch import receiver

from .permissions import (
    GRUPO_CLIENTE,
    GRUPO_FUNCIONARIO,
)


@receiver(post_migrate)
def configurar_grupos_padrao(sender, **kwargs):

    Group.objects.get_or_create(
        name=GRUPO_CLIENTE
    )

    grupo_funcionario, _ = Group.objects.get_or_create(
        name=GRUPO_FUNCIONARIO
    )

    permissoes_funcionario = Permission.objects.filter(
        content_type__app_label__in=[
            "cardapio",
            "estoque",
        ],
        content_type__model__in=[
            "categoriapizza",
            "pizza",
            "categoriaestoque",
            "itemestoque",
            "movimentacaoestoque",
            "receitapizza",
        ],
    )

    grupo_funcionario.permissions.add(
        *permissoes_funcionario
    )