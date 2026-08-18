from django.contrib.auth.models import User
from django.db import models


class Usuario(models.Model):
    usuario = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="perfil",
        verbose_name="usuário",
    )

    telefone = models.CharField(
        max_length=20,
        blank=True,
        verbose_name="telefone",
    )

    cpf = models.CharField(
        max_length=14,
        blank=True,
        null=True,
        unique=True,
        verbose_name="CPF",
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
        verbose_name = "usuário"
        verbose_name_plural = "usuários"
        ordering = ["usuario__username"]

    def __str__(self):
        return self.usuario.get_full_name() or self.usuario.username


class EnderecoUsuario(models.Model):
    usuario = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="enderecos",
        verbose_name="usuário",
    )

    logradouro = models.CharField(
        max_length=255,
        verbose_name="logradouro",
    )

    numero = models.CharField(
        max_length=20,
        blank=True,
        verbose_name="número",
    )

    bairro = models.CharField(
        max_length=100,
        verbose_name="bairro",
    )

    cidade = models.CharField(
        max_length=100,
        verbose_name="cidade",
    )

    estado = models.CharField(
        max_length=2,
        verbose_name="estado",
    )

    complemento = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="complemento",
    )

    referencia = models.CharField(
        max_length=150,
        blank=True,
        verbose_name="referência",
    )

    principal = models.BooleanField(
        default=False,
        verbose_name="endereço principal",
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
        verbose_name = "endereço de usuário"
        verbose_name_plural = "endereços de usuários"

        ordering = [
            "usuario__username",
            "-principal",
            "logradouro",
        ]

    def __str__(self):
        return (
            f"{self.logradouro}, {self.numero} - "
            f"{self.cidade}/{self.estado}"
        )
