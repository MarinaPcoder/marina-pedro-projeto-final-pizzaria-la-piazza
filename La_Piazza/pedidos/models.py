from decimal import Decimal

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models

from pizza.models import Pizza
from usuarios.models import EnderecoUsuario

STATUS_PEDIDO_PENDENTE = "PENDENTE"
STATUS_PEDIDO_CONFIRMADO = "CONFIRMADO"
STATUS_PEDIDO_EM_PREPARO = "EM_PREPARO"
STATUS_PEDIDO_PRONTO = "PRONTO"
STATUS_PEDIDO_SAIU_ENTREGA = "SAIU_ENTREGA"
STATUS_PEDIDO_ENTREGUE = "ENTREGUE"
STATUS_PEDIDO_CANCELADO = "CANCELADO"

STATUS_PEDIDO_CHOICES = (
    (STATUS_PEDIDO_PENDENTE, "Pendente"),
    (STATUS_PEDIDO_CONFIRMADO, "Confirmado"),
    (STATUS_PEDIDO_EM_PREPARO, "Em preparo"),
    (STATUS_PEDIDO_PRONTO, "Pronto"),
    (STATUS_PEDIDO_SAIU_ENTREGA, "Saiu para entrega"),
    (STATUS_PEDIDO_ENTREGUE, "Entregue"),
    (STATUS_PEDIDO_CANCELADO, "Cancelado"),
)

TIPO_ATENDIMENTO_RETIRADA = "RETIRADA"
TIPO_ATENDIMENTO_ENTREGA = "ENTREGA"

TIPO_ATENDIMENTO_CHOICES = (
    (TIPO_ATENDIMENTO_RETIRADA, "Retirada"),
    (TIPO_ATENDIMENTO_ENTREGA, "Entrega"),
)


class Pedido(models.Model):

    usuario = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="pedidos",
        verbose_name="usuário",
    )

    registrado_por = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="pedidos_registrados",
        verbose_name="registrado por",
    )

    origem = models.CharField(
        max_length=10,
        choices=(("SITE", "Site"), ("BALCAO", "Balcão")),
        default="BALCAO",
        verbose_name="origem",
    )

    status = models.CharField(
        max_length=15,
        choices=STATUS_PEDIDO_CHOICES,
        default=STATUS_PEDIDO_PENDENTE,
        verbose_name="status",
    )

    tipo_atendimento = models.CharField(
        max_length=10,
        choices=TIPO_ATENDIMENTO_CHOICES,
        default=TIPO_ATENDIMENTO_RETIRADA,
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

    endereco_entrega_texto = models.TextField(
        blank=True,
        verbose_name="endereço de entrega no pedido",
    )

    estoque_baixado_em = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="estoque baixado em",
    )

    checkout_token = models.UUIDField(null=True, blank=True, unique=True, editable=False)

    concluido_em = models.DateTimeField(null=True, blank=True, editable=False)

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
        nome = (
            self.usuario.get_full_name()
            or self.usuario.username
        )

        return f"Pedido #{self.pk} — {nome}"

    @staticmethod
    def texto_endereco(endereco):
        if endereco is None:
            return ""

        partes = [
            f"{endereco.logradouro}, {endereco.numero}".strip(", "),
            endereco.complemento,
            endereco.bairro,
            f"{endereco.cidade}/{endereco.estado}",
            endereco.referencia,
        ]
        return " - ".join(parte for parte in partes if parte)

    def clean(self):
        # Import local para não carregar views durante a inicialização dos models.
        from usuarios.views import GRUPO_CLIENTE

        erros = {}

        if (
            self.tipo_atendimento == TIPO_ATENDIMENTO_ENTREGA
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
            and not self.usuario.groups.filter(
                name=GRUPO_CLIENTE
            ).exists()
        ):
            erros["usuario"] = (
                "Selecione um usuário do grupo Cliente."
            )

        if erros:
            raise ValidationError(erros)

    @property
    def valor_total(self):
        return sum(
            (
                item.subtotal
                for item in self.itens.all()
            ),
            Decimal("0.00"),
        )

    def baixar_estoque(self, responsavel=None):
        from .views import confirmar_pedido

        if not self.pk:
            raise ValidationError("Salve o pedido antes de confirmar.")
        pedido = confirmar_pedido(self.pk, responsavel)
        self.status = pedido.status
        self.estoque_baixado_em = pedido.estoque_baixado_em



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
        ordering = [
            "pedido",
            "pizza__nome",
        ]

        constraints = [
            models.UniqueConstraint(
                fields=["pedido", "pizza"],
                name="pizza_unica_por_pedido",
            ),
        ]

    def __str__(self):
        return (
            f"{self.quantidade} × "
            f"{self.pizza.nome}"
        )

    @property
    def subtotal(self):
        preco = (
            self.preco_unitario
            or Decimal("0.00")
        )

        return preco * self.quantidade

    def quantidades_estoque_necessarias(self):
        return [
            (
                receita.item_estoque,
                (
                    receita.quantidade_utilizada
                    * self.quantidade
                ),
            )
            for receita
            in self.pizza.receita.select_related(
                "item_estoque"
            )
        ]

    def save(self, *args, **kwargs):
        pizza_alterada = self.pk and ItemPedido.objects.filter(pk=self.pk).exclude(pizza_id=self.pizza_id).exists()
        if self.preco_unitario is None or pizza_alterada:
            self.preco_unitario = self.pizza.preco

        super().save(*args, **kwargs)
