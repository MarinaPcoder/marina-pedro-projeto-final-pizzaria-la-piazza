from django.contrib.auth.models import Group, Permission, User
from django.db.models.signals import post_migrate, post_save
from django.dispatch import receiver
from django.utils import timezone

from .models import Usuario
from .permissions import (
    GRUPO_CLIENTE,
    GRUPO_FUNCIONARIO,
    PERMISSOES_CLIENTE,
    PERMISSOES_FUNCIONARIO,
)


@receiver(
    post_save,
    sender=User,
    dispatch_uid="usuarios.criar_perfil_usuario",
)
def criar_perfil_usuario(sender, instance, created, **kwargs):
    if not created or sender is not User:
        return

    if Usuario.objects.filter(pk=instance.pk).exists():
        return

    agora = timezone.now()
    usuario = Usuario(
        user_ptr_id=instance.pk,
        telefone="",
        observacoes="",
        criado_em=agora,
        atualizado_em=agora,
    )

    # O User pai já foi salvo pelo Django. save_base(raw=True)
    # insere somente a linha filha e evita duplicar auth_user.
    usuario.save_base(
        raw=True,
        using=kwargs.get("using"),
    )


@receiver(
    post_migrate,
    dispatch_uid="usuarios.configurar_grupos_padrao",
)
def configurar_grupos_padrao(sender, **kwargs):
    grupo_cliente, _ = Group.objects.get_or_create(
        name=GRUPO_CLIENTE
    )

    grupo_funcionario, _ = Group.objects.get_or_create(
        name=GRUPO_FUNCIONARIO
    )

    grupo_cliente.permissions.set(
        Permission.objects.filter(
            codename__in=PERMISSOES_CLIENTE,
        )
    )

    grupo_funcionario.permissions.set(
        Permission.objects.filter(
            codename__in=PERMISSOES_FUNCIONARIO,
        )
    )
