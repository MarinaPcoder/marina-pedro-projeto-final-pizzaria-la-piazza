from django.contrib import admin

# Register your models here.

from django.contrib import admin

from .models import (
    CategoriaEstoque,
    ItemEstoque,
    MovimentacaoEstoque,
)


@admin.register(CategoriaEstoque)
class CategoriaEstoqueAdmin(admin.ModelAdmin):
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


@admin.register(ItemEstoque)
class ItemEstoqueAdmin(admin.ModelAdmin):
    list_display = (
        "nome",
        "categoria",
        "quantidade_atual",
        "unidade_medida",
        "estoque_minimo",
        "estoque_baixo",
        "ativo",
    )

    search_fields = (
        "nome",
        "categoria__nome",
    )

    list_filter = (
        "categoria",
        "unidade_medida",
        "ativo",
    )

    ordering = (
        "nome",
    )

    readonly_fields = (
        "criado_em",
        "atualizado_em",
    )

    fieldsets = (
        (
            "Identificação",
            {
                "fields": (
                    "nome",
                    "categoria",
                    "ativo",
                )
            },
        ),
        (
            "Controle de estoque",
            {
                "fields": (
                    "unidade_medida",
                    "quantidade_atual",
                    "estoque_minimo",
                    "preco_custo",
                    "data_validade",
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

    @admin.display(
        boolean=True,
        description="Abaixo do mínimo",
    )
    def estoque_baixo(self, obj):
        return obj.abaixo_do_minimo


@admin.register(MovimentacaoEstoque)
class MovimentacaoEstoqueAdmin(admin.ModelAdmin):
    list_display = (
        "item",
        "tipo",
        "quantidade",
        "responsavel",
        "criada_em",
    )

    search_fields = (
        "item__nome",
        "responsavel__username",
        "responsavel__first_name",
        "responsavel__last_name",
        "motivo",
    )

    list_filter = (
        "tipo",
        "item__categoria",
        "criada_em",
    )

    ordering = (
        "-criada_em",
    )

    readonly_fields = (
        "criada_em",
    )

    date_hierarchy = "criada_em"
