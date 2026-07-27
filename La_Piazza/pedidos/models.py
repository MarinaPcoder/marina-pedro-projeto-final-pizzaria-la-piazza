from django.db import models

# Create your models here.

from decimal import Decimal

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models

from cardapio.models import Pizza
from clientes.models import Cliente


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

    cliente = models.ForeignKey(
        Cliente,
        on_delete=models.PROTECT,
        related_name="pedidos",
        verbose_name="cliente",
    )

    funcionario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="pedidos_registrados",
        verbose_name="funcionário",
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

    endereco_entrega = models.CharField(
        max_length=255,
        blank=True,
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

    class Meta:
        verbose_name = "pedido"
        verbose_name_plural = "pedidos"
        ordering = ["-criado_em"]

    def __str__(self):
        return f"Pedido #{self.pk} — {self.cliente.nome}"

    def clean(self):
        if (
            self.tipo_atendimento == self.TipoAtendimento.ENTREGA
            and not self.endereco_entrega.strip()
        ):
            raise ValidationError(
                {
                    "endereco_entrega": (
                        "Informe o endereço para pedidos de entrega."
                    )
                }
            )

    @property
    def valor_total(self):
        return sum(
            (item.subtotal for item in self.itens.all()),
            Decimal("0.00"),
        )


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

    def save(self, *args, **kwargs):
        if self.preco_unitario is None:
            self.preco_unitario = self.pizza.preco

        super().save(*args, **kwargs)