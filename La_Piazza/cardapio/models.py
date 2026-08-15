from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models

from estoque.models import ItemEstoque


class CategoriaPizza(models.Model):
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
        verbose_name = "categoria de pizza"
        verbose_name_plural = "categorias de pizza"
        ordering = ["nome"]

    def __str__(self):
        return self.nome


class Pizza(models.Model):
    categoria = models.ForeignKey(
        CategoriaPizza,
        on_delete=models.PROTECT,
        related_name="pizzas",
        verbose_name="categoria",
    )

    nome = models.CharField(
        max_length=150,
        unique=True,
        verbose_name="nome",
    )

    descricao = models.TextField(
        blank=True,
        verbose_name="descrição",
    )

    preco = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[
            MinValueValidator(Decimal("0.01"))
        ],
        verbose_name="preço",
    )

    imagem = models.ImageField(
        upload_to="pizzas/",
        null=True,
        blank=True,
        verbose_name="imagem",
    )

    itens_estoque = models.ManyToManyField(
        ItemEstoque,
        through="ReceitaPizza",
        related_name="pizzas",
        verbose_name="itens do estoque",
    )

    disponivel = models.BooleanField(
        default=True,
        verbose_name="disponível",
    )

    criada_em = models.DateTimeField(
        auto_now_add=True,
        verbose_name="criada em",
    )

    atualizada_em = models.DateTimeField(
        auto_now=True,
        verbose_name="atualizada em",
    )

    class Meta:
        verbose_name = "pizza"
        verbose_name_plural = "pizzas"
        ordering = ["nome"]

    def __str__(self):
        return self.nome


class ReceitaPizza(models.Model):
    pizza = models.ForeignKey(
        Pizza,
        on_delete=models.CASCADE,
        related_name="receita",
        verbose_name="pizza",
    )

    item_estoque = models.ForeignKey(
        ItemEstoque,
        on_delete=models.PROTECT,
        related_name="receitas",
        verbose_name="item do estoque",
    )

    quantidade_utilizada = models.DecimalField(
        max_digits=10,
        decimal_places=3,
        validators=[
            MinValueValidator(Decimal("0.001"))
        ],
        verbose_name="quantidade utilizada",
    )

    class Meta:
        verbose_name = "receita da pizza"
        verbose_name_plural = "receitas das pizzas"

        ordering = [
            "pizza__nome",
            "item_estoque__nome",
        ]

        constraints = [
            models.UniqueConstraint(
                fields=["pizza", "item_estoque"],
                name="item_estoque_unico_por_pizza",
            ),
        ]

    def __str__(self):
        return (
            f"{self.pizza.nome} - "
            f"{self.item_estoque.nome}"
        )