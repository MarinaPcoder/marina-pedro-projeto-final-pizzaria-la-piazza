from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.exceptions import ValidationError
from django.test import TestCase
from decimal import Decimal

from cardapio.models import CategoriaPizza, Pizza, ReceitaPizza
from estoque.models import (
    CategoriaEstoque,
    ItemEstoque,
    MovimentacaoEstoque,
)
from usuarios.permissions import GRUPO_CLIENTE

from .models import ItemPedido, Pedido


class PedidoUsuarioTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.grupo_cliente, _ = Group.objects.get_or_create(
            name=GRUPO_CLIENTE,
        )
        self.usuario = User.objects.create_user(
            username="cliente",
            password="senha-teste",
        )
        self.usuario.groups.add(self.grupo_cliente)

    def test_pedido_aceita_usuario_do_grupo_cliente(self):
        pedido = Pedido(usuario=self.usuario)

        pedido.clean()

    def test_pedido_rejeita_usuario_fora_do_grupo_cliente(self):
        self.usuario.groups.clear()
        pedido = Pedido(usuario=self.usuario)

        with self.assertRaises(ValidationError):
            pedido.clean()

    def test_pedido_de_entrega_exige_endereco_do_usuario(self):
        pedido = Pedido(
            usuario=self.usuario,
            tipo_atendimento=Pedido.TipoAtendimento.ENTREGA,
        )

        with self.assertRaises(ValidationError):
            pedido.clean()

    def test_baixar_estoque_desconta_itens_da_receita(self):
        categoria_estoque = CategoriaEstoque.objects.create(
            nome="Laticínios",
        )
        queijo = ItemEstoque.objects.create(
            categoria=categoria_estoque,
            nome="Queijo",
            unidade_medida=ItemEstoque.UnidadeMedida.QUILOGRAMA,
            quantidade_atual="2.000",
        )
        categoria_pizza = CategoriaPizza.objects.create(
            nome="Tradicionais",
        )
        pizza = Pizza.objects.create(
            categoria=categoria_pizza,
            nome="Mussarela",
            preco="40.00",
        )
        ReceitaPizza.objects.create(
            pizza=pizza,
            item_estoque=queijo,
            quantidade_utilizada="0.250",
        )
        pedido = Pedido(
            usuario=self.usuario,
        )
        pedido.save()
        ItemPedido.objects.create(
            pedido=pedido,
            pizza=pizza,
            quantidade=3,
        )

        pedido.baixar_estoque()
        queijo.refresh_from_db()

        self.assertEqual(queijo.quantidade_atual, Decimal("1.250"))
        self.assertEqual(
            MovimentacaoEstoque.objects.filter(
                item=queijo,
                tipo=MovimentacaoEstoque.TipoMovimentacao.SAIDA,
            ).count(),
            1,
        )

        pedido.baixar_estoque()
        queijo.refresh_from_db()

        self.assertEqual(queijo.quantidade_atual, Decimal("1.250"))
