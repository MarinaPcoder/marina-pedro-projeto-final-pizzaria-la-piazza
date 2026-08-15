from django.contrib import admin

# Register your models here.
from django.contrib import admin

from .models import (
    CategoriaPizza,
    Pizza,
    ReceitaPizza,
)


class ReceitaPizzaInline(admin.TabularInline):
    model = ReceitaPizza
    extra = 1

    fields = (
        "item_estoque",
        "quantidade_utilizada",
    )


@admin.register(CategoriaPizza)
class CategoriaPizzaAdmin(admin.ModelAdmin):
    list_display = (
        "nome",
        "ativa",
    )

    search_fields = (
        "nome",
        "descricao",
    )

    list_filter = (
        "ativa",
    )

    ordering = (
        "nome",
    )


@admin.register(Pizza)
class PizzaAdmin(admin.ModelAdmin):
    list_display = (
        "nome",
        "categoria",
        "preco",
        "disponivel",
        "criada_em",
    )

    search_fields = (
        "nome",
        "descricao",
        "categoria__nome",
    )

    list_filter = (
        "categoria",
        "disponivel",
    )

    ordering = (
        "nome",
    )

    readonly_fields = (
        "criada_em",
        "atualizada_em",
    )

    fieldsets = (
        (
            "Informações da pizza",
            {
                "fields": (
                    "nome",
                    "categoria",
                    "descricao",
                    "preco",
                )
            },
        ),
        (
            "Apresentação",
            {
                "fields": (
                    "imagem",
                    "disponivel",
                )
            },
        ),
        (
            "Auditoria",
            {
                "fields": (
                    "criada_em",
                    "atualizada_em",
                )
            },
        ),
    )

    inlines = [
        ReceitaPizzaInline,
    ]


@admin.register(ReceitaPizza)
class ReceitaPizzaAdmin(admin.ModelAdmin):
    list_display = (
        "pizza",
        "item_estoque",
        "quantidade_utilizada",
    )

    search_fields = (
        "pizza__nome",
        "item_estoque__nome",
    )

    list_filter = (
        "pizza",
        "item_estoque__categoria",
    )

    ordering = (
        "pizza__nome",
        "item_estoque__nome",
    )