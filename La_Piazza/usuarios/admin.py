from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

from .models import EnderecoUsuario, Usuario


class UsuarioInline(admin.StackedInline):
    model = Usuario
    fk_name = "user_ptr"
    extra = 0
    fields = (
        "telefone",
        "cpf",
        "observacoes",
        "criado_em",
        "atualizado_em",
    )
    readonly_fields = (
        "criado_em",
        "atualizado_em",
    )


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


admin.site.unregister(User)


@admin.register(User)
class UsuarioAdmin(UserAdmin):
    list_display = (
        "username",
        "first_name",
        "last_name",
        "email",
        "telefone_display",
        "cpf_display",
        "is_staff",
        "is_active",
    )

    search_fields = (
        "username",
        "first_name",
        "last_name",
        "email",
        "usuario__telefone",
        "usuario__cpf",
    )

    list_filter = (
        "is_active",
        "is_staff",
        "is_superuser",
        "groups",
    )

    ordering = ("username",)

    inlines = [
        UsuarioInline,
        EnderecoUsuarioInline,
    ]

    @admin.display(description="telefone")
    def telefone_display(self, obj):
        return getattr(getattr(obj, "usuario", None), "telefone", "")

    @admin.display(description="CPF")
    def cpf_display(self, obj):
        return getattr(getattr(obj, "usuario", None), "cpf", "") or ""


@admin.register(Usuario)
class UsuarioPerfilAdmin(admin.ModelAdmin):
    list_display = (
        "username",
        "telefone",
        "cpf",
        "criado_em",
        "atualizado_em",
    )
    search_fields = (
        "username",
        "first_name",
        "last_name",
        "email",
        "telefone",
        "cpf",
    )


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
