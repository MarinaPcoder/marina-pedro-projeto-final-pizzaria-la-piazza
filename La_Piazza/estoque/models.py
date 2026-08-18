from decimal import Decimal

from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.db import models


UNIDADE_MEDIDA_UNIDADE = "UN"
UNIDADE_MEDIDA_QUILOGRAMA = "KG"
UNIDADE_MEDIDA_GRAMA = "G"
UNIDADE_MEDIDA_LITRO = "L"
UNIDADE_MEDIDA_MILILITRO = "ML"
UNIDADE_MEDIDA_PACOTE = "PCT"
UNIDADE_MEDIDA_CAIXA = "CX"

UNIDADE_MEDIDA_CHOICES = (
    (UNIDADE_MEDIDA_UNIDADE, "Unidade"),
    (UNIDADE_MEDIDA_QUILOGRAMA, "Quilograma"),
    (UNIDADE_MEDIDA_GRAMA, "Grama"),
    (UNIDADE_MEDIDA_LITRO, "Litro"),
    (UNIDADE_MEDIDA_MILILITRO, "Mililitro"),
    (UNIDADE_MEDIDA_PACOTE, "Pacote"),
    (UNIDADE_MEDIDA_CAIXA, "Caixa"),
)

TIPO_MOVIMENTACAO_ENTRADA = "ENTRADA"
TIPO_MOVIMENTACAO_SAIDA = "SAIDA"
TIPO_MOVIMENTACAO_PERDA = "PERDA"
TIPO_MOVIMENTACAO_AJUSTE = "AJUSTE"

TIPO_MOVIMENTACAO_CHOICES = (
    (TIPO_MOVIMENTACAO_ENTRADA, "Entrada"),
    (TIPO_MOVIMENTACAO_SAIDA, "Saída"),
    (TIPO_MOVIMENTACAO_PERDA, "Perda"),
    (TIPO_MOVIMENTACAO_AJUSTE, "Ajuste"),
)


class CategoriaEstoque(models.Model):
    nome = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="nome",
    )

    descricao = models.TextField(
        blank=True,
        verbose_name="descrição",
    )

    ativa = models.BooleanField(
        default=True,
        verbose_name="ativa",
    )

    class Meta:
        verbose_name = "categoria de estoque"
        verbose_name_plural = "categorias de estoque"
        ordering = ["nome"]

    def __str__(self):
        return self.nome


class ItemEstoque(models.Model):
    categoria = models.ForeignKey(
        CategoriaEstoque,
        on_delete=models.PROTECT,
        related_name="itens",
        verbose_name="categoria",
    )

    nome = models.CharField(
        max_length=150,
        unique=True,
        verbose_name="nome",
    )

    unidade_medida = models.CharField(
        max_length=3,
        choices=UNIDADE_MEDIDA_CHOICES,
        default=UNIDADE_MEDIDA_UNIDADE,
        verbose_name="unidade de medida",
    )

    quantidade_atual = models.DecimalField(
        max_digits=10,
        decimal_places=3,
        default=Decimal("0.000"),
        validators=[
            MinValueValidator(Decimal("0.000"))
        ],
        verbose_name="quantidade atual",
    )

    estoque_minimo = models.DecimalField(
        max_digits=10,
        decimal_places=3,
        default=Decimal("0.000"),
        validators=[
            MinValueValidator(Decimal("0.000"))
        ],
        verbose_name="estoque mínimo",
    )

    preco_custo = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[
            MinValueValidator(Decimal("0.00"))
        ],
        verbose_name="preço de custo",
    )

    data_validade = models.DateField(
        null=True,
        blank=True,
        verbose_name="data de validade",
    )

    ativo = models.BooleanField(
        default=True,
        verbose_name="ativo",
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
        verbose_name = "item do estoque"
        verbose_name_plural = "itens do estoque"
        ordering = ["nome"]

    def __str__(self):
        return (
            f"{self.nome} — "
            f"{self.quantidade_atual} "
            f"{self.get_unidade_medida_display()}"
        )

    @property
    def abaixo_do_minimo(self):
        return (
            self.quantidade_atual
            <= self.estoque_minimo
        )


class MovimentacaoEstoque(models.Model):
    item = models.ForeignKey(
        ItemEstoque,
        on_delete=models.PROTECT,
        related_name="movimentacoes",
        verbose_name="item",
    )

    tipo = models.CharField(
        max_length=10,
        choices=TIPO_MOVIMENTACAO_CHOICES,
        verbose_name="tipo",
    )

    quantidade = models.DecimalField(
        max_digits=10,
        decimal_places=3,
        validators=[
            MinValueValidator(Decimal("0.001"))
        ],
        verbose_name="quantidade",
    )

    responsavel = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="movimentacoes_estoque",
        verbose_name="responsável",
    )

    motivo = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="motivo",
    )

    criada_em = models.DateTimeField(
        auto_now_add=True,
        verbose_name="criada em",
    )

    class Meta:
        verbose_name = "movimentação de estoque"
        verbose_name_plural = "movimentações de estoque"
        ordering = ["-criada_em"]

    def __str__(self):
        return (
            f"{self.get_tipo_display()} — "
            f"{self.item.nome}"
        )
