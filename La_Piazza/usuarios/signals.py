from django.contrib.auth.models import Group, Permission
from django.db.models.signals import post_migrate
from django.dispatch import receiver

from .permissions import (
    GRUPO_CLIENTE,
    GRUPO_FUNCIONARIO,
)


@receiver(post_migrate)
def configurar_grupos_padrao(sender, **kwargs):
    """
    Cria os grupos padrão do sistema e entrega
    as permissões de gerenciamento do cardápio
    ao grupo Funcionário.
    """

    grupo_cliente, _ = Group.objects.get_or_create(
        name=GRUPO_CLIENTE
    )

    grupo_funcionario, _ = Group.objects.get_or_create(
        name=GRUPO_FUNCIONARIO
    )

    permissoes_cardapio = Permission.objects.filter(
        content_type__app_label="cardapio",
        content_type__model__in=[
            "categoriapizza",
            "pizza",
        ],
    )

    grupo_funcionario.permissions.add(
        *permissoes_cardapio
    )