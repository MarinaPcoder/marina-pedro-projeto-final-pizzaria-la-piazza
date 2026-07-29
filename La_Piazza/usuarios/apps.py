from django.apps import AppConfig


class UsuariosConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "usuarios"
    verbose_name = "usuários"

    def ready(self):
        from django.db.models.signals import post_migrate

        from .permissions import criar_grupos_e_permissoes

        post_migrate.connect(
            criar_grupos_e_permissoes,
            dispatch_uid="usuarios.criar_grupos_e_permissoes",
        )
