from django.urls import path

from . import views


urlpatterns = [
    # PÁGINAS PÚBLICAS

    path(
        "",
        views.index,
        name="index",
    ),

    path(
        "menu/",
        views.menu,
        name="menu",
    ),

    path(
        "sobre/",
        views.sobre,
        name="sobre",
    ),


    # =========================
    # CATEGORIAS DE PIZZA
    # =========================

    path(
        "gerenciamento/categorias/",
        views.categoria_lista,
        name="categoria_lista",
    ),

    path(
        "gerenciamento/categorias/nova/",
        views.categoria_criar,
        name="categoria_criar",
    ),

    path(
        "gerenciamento/categorias/<int:pk>/",
        views.categoria_detalhe,
        name="categoria_detalhe",
    ),

    path(
        "gerenciamento/categorias/<int:pk>/editar/",
        views.categoria_editar,
        name="categoria_editar",
    ),

    path(
        "gerenciamento/categorias/<int:pk>/excluir/",
        views.categoria_excluir,
        name="categoria_excluir",
    ),


    # =========================
    # PIZZAS
    # =========================

    path(
        "gerenciamento/pizzas/",
        views.pizza_lista,
        name="pizza_lista",
    ),

    path(
        "gerenciamento/pizzas/nova/",
        views.pizza_criar,
        name="pizza_criar",
    ),

    path(
        "gerenciamento/pizzas/<int:pk>/",
        views.pizza_detalhe,
        name="pizza_detalhe",
    ),

    path(
        "gerenciamento/pizzas/<int:pk>/editar/",
        views.pizza_editar,
        name="pizza_editar",
    ),

    path(
        "gerenciamento/pizzas/<int:pk>/excluir/",
        views.pizza_excluir,
        name="pizza_excluir",
    ),
]