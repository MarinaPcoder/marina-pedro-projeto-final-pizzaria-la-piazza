from django.db import models

# Create your models here.

from django.db import models


class Cliente(models.Model):
    nome = models.CharField(
        max_length=150,
        verbose_name="nome",
    )

    telefone = models.CharField(
        max_length=20,
        db_index=True,
        verbose_name="telefone",
    )

    email = models.EmailField(
        blank=True,
        verbose_name="e-mail",
    )

    endereco = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="endereço",
    )

    complemento = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="complemento",
    )

    observacoes = models.TextField(
        blank=True,
        verbose_name="observações",
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
        verbose_name = "cliente"
        verbose_name_plural = "clientes"
        ordering = ["nome"]

    def __str__(self):
        return self.nome