from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import EnderecoUsuario, Usuario


@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        (
            "Dados do usuário",
            {
                "fields": (
                    "telefone",
                    "cpf",
                    "observacoes",
                )
            },
        ),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        (
            "Dados do usuário",
            {
                "fields": (
                    "telefone",
                    "cpf",
                )
            },
        ),
    )

    list_display = (
        "username",
        "email",
        "first_name",
        "last_name",
        "telefone",
        "cpf",
        "is_staff",
    )
    search_fields = UserAdmin.search_fields + ("telefone", "cpf")


admin.site.register(EnderecoUsuario)
