from django.urls import path

from . import views


app_name = "estoque"


urlpatterns = [
    path(
        "categorias/",
        views.categoria_lista,
        name="categoria_lista",
    ),

    path(
        "categorias/nova/",
        views.categoria_criar,
        name="categoria_criar",
    ),

    path(
        "categorias/<int:pk>/",
        views.categoria_detalhe,
        name="categoria_detalhe",
    ),

    path(
        "categorias/<int:pk>/editar/",
        views.categoria_editar,
        name="categoria_editar",
    ),

    path(
        "categorias/<int:pk>/excluir/",
        views.categoria_excluir,
        name="categoria_excluir",
    ),

        # =========================
    # ITENS DE ESTOQUE
    # =========================

    path(
        "itens/",
        views.item_lista,
        name="item_lista",
    ),

    path(
        "itens/novo/",
        views.item_criar,
        name="item_criar",
    ),

    path(
        "itens/<int:pk>/",
        views.item_detalhe,
        name="item_detalhe",
    ),

    path(
        "itens/<int:pk>/editar/",
        views.item_editar,
        name="item_editar",
    ),

    path(
        "itens/<int:pk>/excluir/",
        views.item_excluir,
        name="item_excluir",
    ),

    path(
    "movimentacoes/",
    views.movimentacao_lista,
    name="movimentacao_lista",
    ),

    path(
    "movimentacoes/nova/",
    views.movimentacao_criar,
    name="movimentacao_criar",
    ),

]