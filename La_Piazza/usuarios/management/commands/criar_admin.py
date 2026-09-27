import os
from getpass import getpass

from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.contrib.auth.models import User

from usuarios.models import Usuario


class Command(BaseCommand):
    help = "Cria um administrador sem senha fixa; preserva contas existentes."

    def add_arguments(self, parser):
        parser.add_argument("--username", default="admin")
        parser.add_argument("--email", default="")
        parser.add_argument("--noinput", action="store_true")

    @transaction.atomic
    def handle(self, *args, **options):
        existente = User.objects.filter(username=options["username"]).first()
        if existente:
            if not existente.is_superuser:
                raise CommandError("O nome ja pertence a uma conta comum. Escolha outro nome.")
            self.stdout.write("Administrador ja existe; senha e dados preservados.")
            return
        senha = os.environ.get("DJANGO_SUPERUSER_PASSWORD")
        if not senha and not options["noinput"]:
            senha = getpass("Senha do administrador: ")
            if senha != getpass("Repita a senha: "):
                raise CommandError("As senhas nao coincidem.")
        if not senha:
            raise CommandError("Defina DJANGO_SUPERUSER_PASSWORD ou execute sem --noinput.")
        usuario = Usuario(username=options["username"], email=options["email"])
        try:
            validate_password(senha, usuario)
        except ValidationError as erro:
            raise CommandError(" ".join(erro.messages)) from erro
        Usuario.objects.create_superuser(username=options["username"], email=options["email"], password=senha)
        self.stdout.write(self.style.SUCCESS("Administrador criado."))
