from django.contrib import admin

# Register your models here.

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import EnderecoUsuario, Usuario


class EnderecoUsuarioInline(admin.TabularInline):
    model = EnderecoUsuario
    extra = 0

    fields = (
        "logradouro",
        "numero",
        "bairro",
        "cidade",
        "estado",
        "principal",
        "ativo",
    )


@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    list_display = (
        "username",
        "first_name",
        "last_name",
        "email",
        "telefone",
        "cpf",
        "is_staff",
        "is_active",
    )

    search_fields = (
        "username",
        "first_name",
        "last_name",
        "email",
        "telefone",
        "cpf",
    )

    list_filter = (
        "is_active",
        "is_staff",
        "is_superuser",
        "groups",
    )

    ordering = ("username",)

    readonly_fields = (
        "criado_em",
        "atualizado_em",
    )

    fieldsets = UserAdmin.fieldsets + (
        (
            "Dados do La Piazza",
            {
                "fields": (
                    "telefone",
                    "cpf",
                    "observacoes",
                )
            },
        ),
        (
            "Auditoria",
            {
                "fields": (
                    "criado_em",
                    "atualizado_em",
                )
            },
        ),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        (
            "Dados do La Piazza",
            {
                "fields": (
                    "first_name",
                    "last_name",
                    "email",
                    "telefone",
                    "cpf",
                )
            },
        ),
    )

    inlines = [
        EnderecoUsuarioInline,
    ]


@admin.register(EnderecoUsuario)
class EnderecoUsuarioAdmin(admin.ModelAdmin):
    list_display = (
        "usuario",
        "logradouro",
        "numero",
        "bairro",
        "cidade",
        "estado",
        "principal",
        "ativo",
    )

    search_fields = (
        "usuario__username",
        "usuario__first_name",
        "usuario__last_name",
        "logradouro",
        "bairro",
        "cidade",
    )

    list_filter = (
        "estado",
        "principal",
        "ativo",
    )

    ordering = (
        "usuario__username",
        "-principal",
    )
