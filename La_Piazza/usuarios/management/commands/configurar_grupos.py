from django.contrib.auth.models import Group, Permission
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from usuarios.permissions import (
    GRUPO_CLIENTE, GRUPO_FUNCIONARIO, PERMISSOES_CLIENTE, PERMISSOES_FUNCIONARIO,
)


class Command(BaseCommand):
    help = "Cria/sincroniza os grupos Cliente e Funcionario com as permissoes do projeto."

    @transaction.atomic
    def handle(self, *args, **options):
        for nome, codenames in ((GRUPO_CLIENTE, PERMISSOES_CLIENTE), (GRUPO_FUNCIONARIO, PERMISSOES_FUNCIONARIO)):
            permissoes = Permission.objects.filter(
                content_type__app_label__in=["auth", "usuarios", "pedidos", "cardapio", "estoque"],
                codename__in=codenames,
            )
            faltantes = set(codenames) - set(permissoes.values_list("codename", flat=True))
            if faltantes:
                raise CommandError("Execute migrate antes: permissoes ausentes: " + ", ".join(sorted(faltantes)))
            grupo, _ = Group.objects.get_or_create(name=nome)
            grupo.permissions.set(permissoes)
            self.stdout.write(self.style.SUCCESS(f"{nome}: {permissoes.count()} permissoes configuradas."))
