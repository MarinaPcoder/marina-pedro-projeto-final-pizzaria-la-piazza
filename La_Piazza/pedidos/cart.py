from decimal import Decimal
from uuid import uuid4

from pizza.models import Pizza


CART_KEY = "carrinho"


def itens_carrinho(session):
    carrinho = session.get(CART_KEY, {})
    pizzas = {str(p.pk): p for p in Pizza.objects.filter(pk__in=carrinho).select_related("categoria")}
    itens = []
    for chave, dado in carrinho.items():
        pizza = pizzas.get(chave)
        quantidade = dado["quantidade"]
        if pizza is None:
            itens.append({
                "pizza": {"pk": int(chave), "nome": "Pizza removida do cardapio", "preco": Decimal(dado["preco"])},
                "quantidade": quantidade, "subtotal": Decimal(dado["preco"]) * quantidade,
                "disponivel": False, "preco_alterado": False,
            })
            continue
        itens.append({
            "pizza": pizza,
            "quantidade": quantidade,
            "subtotal": pizza.preco * quantidade,
            "disponivel": pizza.disponivel and pizza.categoria.ativa,
            "preco_alterado": Decimal(dado["preco"]) != pizza.preco,
        })
    return itens


def total_carrinho(itens):
    return sum((item["subtotal"] for item in itens), Decimal("0.00"))


def salvar_carrinho(session, carrinho):
    session[CART_KEY] = carrinho
    session["checkout_token"] = str(uuid4())
