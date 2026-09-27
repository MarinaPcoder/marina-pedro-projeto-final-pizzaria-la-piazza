from django.contrib import admin

from .models import ItemPedido, Pedido


class ConsultaPedidoAdmin(admin.ModelAdmin):
    # Alteracoes operacionais passam pelas views que bloqueiam o pedido e validam o fluxo.
    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class ItemPedidoInline(admin.TabularInline):
    model = ItemPedido
    extra = 1

    fields = (
        "pizza",
        "quantidade",
        "preco_unitario",
    )

    readonly_fields = (
        "pizza",
        "quantidade",
        "preco_unitario",
    )

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Pedido)
class PedidoAdmin(ConsultaPedidoAdmin):
    list_display = (
        "id",
        "usuario",
        "registrado_por",
        "origem",
        "status",
        "tipo_atendimento",
        "endereco_entrega",
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
        "registrado_por",
        "origem",
        "endereco_entrega_texto",
        "estoque_baixado_em",
        "concluido_em",
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
                    "endereco_entrega",
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
                    "registrado_por",
                    "origem",
                    "endereco_entrega_texto",
                    "estoque_baixado_em",
                    "concluido_em",
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
class ItemPedidoAdmin(ConsultaPedidoAdmin):
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
