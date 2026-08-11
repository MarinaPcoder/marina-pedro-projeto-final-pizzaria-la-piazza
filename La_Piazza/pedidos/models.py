from decimal import Decimal

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models, transaction

from cardapio.models import Pizza
from estoque.models import ItemEstoque, MovimentacaoEstoque
from usuarios.models import EnderecoUsuario, Usuario
from usuarios.permissions import GRUPO_CLIENTE, GRUPO_FUNCIONARIO


class Pedido(models.Model):
    class StatusPedido(models.TextChoices):
        PENDENTE = "PENDENTE", "Pendente"
        CONFIRMADO = "CONFIRMADO", "Confirmado"
        EM_PREPARO = "EM_PREPARO", "Em preparo"
        PRONTO = "PRONTO", "Pronto"
        SAIU_ENTREGA = "SAIU_ENTREGA", "Saiu para entrega"
        ENTREGUE = "ENTREGUE", "Entregue"
        CANCELADO = "CANCELADO", "Cancelado"

    class TipoAtendimento(models.TextChoices):
        RETIRADA = "RETIRADA", "Retirada"
        ENTREGA = "ENTREGA", "Entrega"

    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.PROTECT,
        related_name="pedidos",
        verbose_name="usuário",
    )

    status = models.CharField(
        max_length=15,
        choices=StatusPedido.choices,
        default=StatusPedido.PENDENTE,
        verbose_name="status",
    )

    tipo_atendimento = models.CharField(
        max_length=10,
        choices=TipoAtendimento.choices,
        default=TipoAtendimento.RETIRADA,
        verbose_name="tipo de atendimento",
    )

    endereco_entrega = models.ForeignKey(
        EnderecoUsuario,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="pedidos",
        verbose_name="endereço de entrega",
    )

    observacoes = models.TextField(
        blank=True,
        verbose_name="observações",
    )

    criado_em = models.DateTimeField(
        auto_now_add=True,
        verbose_name="criado em",
    )

    atualizado_em = models.DateTimeField(
        auto_now=True,
        verbose_name="atualizado em",
    )

    estoque_baixado = models.BooleanField(
        default=False,
        verbose_name="estoque baixado",
    )

    class Meta:
        verbose_name = "pedido"
        verbose_name_plural = "pedidos"
        ordering = ["-criado_em"]

    def __str__(self):
        usuario = self.usuario.get_full_name() or self.usuario.username
        return f"Pedido #{self.pk} — {usuario}"

    def clean(self):
        erros = {}

        if (
            self.tipo_atendimento == self.TipoAtendimento.ENTREGA
            and not self.endereco_entrega_id
        ):
            erros["endereco_entrega"] = (
                "Informe o endereço para pedidos de entrega."
            )

        if (
            self.endereco_entrega_id
            and self.usuario_id
            and self.endereco_entrega.usuario_id != self.usuario_id
        ):
            erros["endereco_entrega"] = (
                "Selecione um endereço cadastrado para este usuário."
            )

        if (
            self.usuario_id
            and not self.usuario.groups.filter(name=GRUPO_CLIENTE).exists()
        ):
            erros["usuario"] = "Selecione um usuário do grupo Cliente."

        if (
            self.usuario_id
            and self.usuario.groups.filter(name=GRUPO_FUNCIONARIO).exists()
        ):
            erros["usuario"] = (
                "Funcionários não devem ser usados como comprador do pedido."
            )

        if erros:
            raise ValidationError(erros)

    @property
    def valor_total(self):
        return sum(
            (item.subtotal for item in self.itens.all()),
            Decimal("0.00"),
        )

    def baixar_estoque(self, responsavel=None):
        if not self.pk:
            raise ValidationError("Salve o pedido antes de baixar o estoque.")

        with transaction.atomic():
            pedido = (
                Pedido.objects.select_for_update()
                .select_related("usuario")
                .get(pk=self.pk)
            )

            if pedido.estoque_baixado:
                return

            for item_pedido in pedido.itens.select_related("pizza"):
                for receita in item_pedido.pizza.receita.select_related(
                    "item_estoque",
                ):
                    quantidade = (
                        receita.quantidade_utilizada
                        * item_pedido.quantidade
                    )
                    item_estoque = ItemEstoque.objects.select_for_update().get(
                        pk=receita.item_estoque_id,
                    )

                    if item_estoque.quantidade_atual < quantidade:
                        raise ValidationError(
                            {
                                "estoque": (
                                    f"Estoque insuficiente para "
                                    f"{item_estoque.nome}."
                                )
                            }
                        )

                    item_estoque.quantidade_atual -= quantidade
                    item_estoque.save(
                        update_fields=[
                            "quantidade_atual",
                            "atualizado_em",
                        ]
                    )

                    MovimentacaoEstoque.objects.create(
                        item=item_estoque,
                        tipo=MovimentacaoEstoque.TipoMovimentacao.SAIDA,
                        quantidade=quantidade,
                        responsavel=responsavel or pedido.usuario,
                        motivo=f"Baixa automática do Pedido #{pedido.pk}",
                    )

            pedido.estoque_baixado = True
            pedido.save(
                update_fields=[
                    "estoque_baixado",
                    "atualizado_em",
                ]
            )
            self.estoque_baixado = True


class ItemPedido(models.Model):
    pedido = models.ForeignKey(
        Pedido,
        on_delete=models.CASCADE,
        related_name="itens",
        verbose_name="pedido",
    )

    pizza = models.ForeignKey(
        Pizza,
        on_delete=models.PROTECT,
        related_name="itens_pedido",
        verbose_name="pizza",
    )

    quantidade = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1)],
        verbose_name="quantidade",
    )

    preco_unitario = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="preço unitário",
    )

    class Meta:
        verbose_name = "item do pedido"
        verbose_name_plural = "itens do pedido"
        ordering = ["pedido", "pizza__nome"]

        constraints = [
            models.UniqueConstraint(
                fields=["pedido", "pizza"],
                name="pizza_unica_por_pedido",
            ),
        ]

    def __str__(self):
        return f"{self.quantidade} × {self.pizza.nome}"

    @property
    def subtotal(self):
        preco = self.preco_unitario or Decimal("0.00")
        return preco * self.quantidade

    def quantidades_estoque_necessarias(self):
        return [
            (
                receita.item_estoque,
                receita.quantidade_utilizada * self.quantidade,
            )
            for receita in self.pizza.receita.select_related("item_estoque")
        ]

    def save(self, *args, **kwargs):
        if self.preco_unitario is None:
            self.preco_unitario = self.pizza.preco

        super().save(*args, **kwargs)
