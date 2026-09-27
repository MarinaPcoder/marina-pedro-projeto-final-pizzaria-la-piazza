from django.urls import path

from . import views


app_name = "pedidos"


# Rotas do gerenciamento de pedidos
urlpatterns = [
    path("<int:pk>/status/", views.pedido_status, name="pedido_status"),
    path(
        "",
        views.pedido_lista,
        name="pedido_lista",
    ),

    path(
        "novo/",
        views.pedido_criar,
        name="pedido_criar",
    ),

    path(
        "<int:pk>/",
        views.pedido_detalhe,
        name="pedido_detalhe",
    ),

    path(
        "<int:pk>/editar/",
        views.pedido_editar,
        name="pedido_editar",
    ),

    path(
        "<int:pk>/excluir/",
        views.pedido_excluir,
        name="pedido_excluir",
    ),

    # =========================
    # ITENS DO PEDIDO
    # =========================

    path(
        "itens/",
        views.item_lista,
        name="item_lista",
    ),

    path(
        "<int:pedido_pk>/itens/adicionar/",
        views.item_adicionar,
        name="item_adicionar",
    ),

    path(
        "<int:pedido_pk>/itens/<int:item_pk>/editar/",
        views.item_editar,
        name="item_editar",
    ),

    path(
        "<int:pedido_pk>/itens/<int:item_pk>/excluir/",
        views.item_excluir,
        name="item_excluir",
    ),

    path(
    "<int:pk>/confirmar/",
    views.pedido_confirmar,
    name="pedido_confirmar",
    ),
]


# Rotas da compra pública (incluídas com o namespace "compras")
compras_urlpatterns = [
    path("carrinho/", views.carrinho, name="carrinho"),
    path("carrinho/adicionar/<int:pizza_pk>/", views.carrinho_adicionar, name="adicionar"),
    path("carrinho/atualizar/<int:pizza_pk>/", views.carrinho_atualizar, name="atualizar"),
    path("checkout/", views.checkout, name="checkout"),
    path("meus-pedidos/", views.meus_pedidos, name="lista"),
    path("meus-pedidos/<int:pk>/", views.detalhe, name="detalhe"),
    path("meus-pedidos/<int:pk>/cancelar/", views.cancelar, name="cancelar"),
]
