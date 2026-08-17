from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import transaction

from .models import (
    ItemEstoque,
    MovimentacaoEstoque,
)


@transaction.atomic
def registrar_movimentacao(
    *,
    item,
    tipo,
    quantidade,
    responsavel,
    motivo="",
):

    item = (
        ItemEstoque.objects
        .select_for_update()
        .get(pk=item.pk)
    )

    quantidade = Decimal(quantidade)

    if quantidade <= 0:
        raise ValidationError(
            "A quantidade deve ser maior que zero."
        )


    # ENTRADA
    if tipo == MovimentacaoEstoque.TipoMovimentacao.ENTRADA:

        item.quantidade_atual += quantidade


    # SAÍDA
    elif tipo == MovimentacaoEstoque.TipoMovimentacao.SAIDA:

        if quantidade > item.quantidade_atual:

            raise ValidationError(
                (
                    f"Estoque insuficiente de {item.nome}. "
                    f"Disponível: {item.quantidade_atual}."
                )
            )

        item.quantidade_atual -= quantidade


    # PERDA
    elif tipo == MovimentacaoEstoque.TipoMovimentacao.PERDA:

        if quantidade > item.quantidade_atual:

            raise ValidationError(
                (
                    f"A perda informada é maior que o "
                    f"estoque disponível de {item.nome}."
                )
            )

        item.quantidade_atual -= quantidade


    # AJUSTE
    elif tipo == MovimentacaoEstoque.TipoMovimentacao.AJUSTE:

        item.quantidade_atual = quantidade


    else:

        raise ValidationError(
            "Tipo de movimentação inválido."
        )


    item.save()


    movimentacao = MovimentacaoEstoque.objects.create(
        item=item,
        tipo=tipo,
        quantidade=quantidade,
        responsavel=responsavel,
        motivo=motivo,
    )

    return movimentacao