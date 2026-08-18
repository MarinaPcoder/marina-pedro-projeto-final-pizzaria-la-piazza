from django.contrib import admin

# Register your models here.

from django.contrib import admin

from .models import ItemPedido, Pedido


class ItemPedidoInline(admin.TabularInline):
    model = ItemPedido
    extra = 1

    fields = (
        "pizza",
        "quantidade",
        "preco_unitario",
    )

    readonly_fields = (
        "preco_unitario",
    )


@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "usuario",
        "status",
        "tipo_atendimento",
        "valor_total_admin",
        "criado_em",
    )

    search_fields = (
        "usuario__username",
        "usuario__first_name",
        "usuario__last_name",
    )

    list_filter = (
        "status",
        "tipo_atendimento",
        "criado_em",
    )

    ordering = (
        "-criado_em",
    )

    readonly_fields = (
        "valor_total_admin",
        "criado_em",
        "atualizado_em",
    )

    fieldsets = (
        (
            "Pedido",
            {
                "fields": (
                    "usuario",
                    "status",
                    "tipo_atendimento",
                    "observacoes",
                )
            },
        ),
        (
            "Valores",
            {
                "fields": (
                    "valor_total_admin",
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

    inlines = [
        ItemPedidoInline,
    ]

    date_hierarchy = "criado_em"

    @admin.display(
        description="Valor total",
    )
    def valor_total_admin(self, obj):
        return obj.valor_total


@admin.register(ItemPedido)
class ItemPedidoAdmin(admin.ModelAdmin):
    list_display = (
        "pedido",
        "pizza",
        "quantidade",
        "preco_unitario",
        "subtotal_admin",
    )

    search_fields = (
        "pizza__nome",
        "pedido__usuario__username",
    )

    list_filter = (
        "pizza__categoria",
    )

    ordering = (
        "-pedido__criado_em",
    )

    @admin.display(
        description="Subtotal",
    )
    def subtotal_admin(self, obj):
        return obj.subtotal
