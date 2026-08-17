from django.urls import path

from . import views


app_name = "pedidos"


urlpatterns = [
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