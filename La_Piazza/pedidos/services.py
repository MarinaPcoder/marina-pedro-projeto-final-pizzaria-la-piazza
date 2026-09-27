from collections import defaultdict
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from estoque.models import ItemEstoque, TIPO_MOVIMENTACAO_SAIDA
from estoque.services import registrar_movimentacao
from .models import Pedido


def garantir_editavel(pedido):
    if pedido.status != "PENDENTE" or pedido.estoque_baixado_em:
        raise ValidationError("Somente pedidos pendentes podem ser alterados.")


def proximos_status(pedido):
    fluxo = {
        "PENDENTE": ("CANCELADO",),
        "CONFIRMADO": ("EM_PREPARO",),
        "EM_PREPARO": ("PRONTO",),
        "PRONTO": (("SAIU_ENTREGA",) if pedido.tipo_atendimento == "ENTREGA" else ("ENTREGUE",)),
        "SAIU_ENTREGA": ("ENTREGUE",),
    }
    return fluxo.get(pedido.status, ())


@transaction.atomic
def confirmar_pedido(pk, responsavel=None):
    pedido = Pedido.objects.select_for_update().get(pk=pk)
    garantir_editavel(pedido)
    itens = list(pedido.itens.select_related("pizza__categoria").prefetch_related("pizza__receita"))
    if not itens:
        raise ValidationError("Adicione pizzas antes de confirmar o pedido.")

    necessidades = defaultdict(Decimal)
    for item in itens:
        receitas = list(item.pizza.receita.all())
        if not item.pizza.disponivel or not item.pizza.categoria.ativa or not receitas:
            raise ValidationError(f"{item.pizza.nome}: pizza indisponivel ou sem receita.")
        for receita in receitas:
            if receita.quantidade_utilizada <= 0:
                raise ValidationError("Corrija as quantidades da receita antes de confirmar.")
            necessidades[receita.item_estoque_id] += receita.quantidade_utilizada * item.quantidade

    # A ordem fixa de bloqueio reduz disputas entre pedidos com ingredientes em comum.
    for item_id, quantidade in sorted(necessidades.items()):
        estoque = ItemEstoque.objects.select_for_update().get(pk=item_id)
        if not estoque.ativo or (estoque.data_validade and estoque.data_validade < timezone.localdate()):
            raise ValidationError(f"Ingrediente inativo ou vencido: {estoque.nome}.")
        registrar_movimentacao(
            item=estoque, tipo=TIPO_MOVIMENTACAO_SAIDA, quantidade=quantidade,
            responsavel=responsavel, motivo=f"Baixa do Pedido #{pedido.pk}",
        )

    pedido.status = "CONFIRMADO"
    pedido.estoque_baixado_em = timezone.now()
    pedido.save(update_fields=["status", "estoque_baixado_em", "atualizado_em"])
    return pedido


@transaction.atomic
def alterar_status(pk, status, usuario=None):
    pedido = Pedido.objects.select_for_update().get(pk=pk)
    if usuario is not None and pedido.usuario_id != usuario.pk:
        raise ValidationError("Este pedido pertence a outro usuario.")
    if status not in proximos_status(pedido):
        raise ValidationError("Transicao de status nao permitida.")
    pedido.status = status
    if status == "ENTREGUE":
        pedido.concluido_em = timezone.now()
    pedido.save(update_fields=["status", "concluido_em", "atualizado_em"])
    return pedido
