from django.urls import path

from . import views


app_name = "usuarios"


urlpatterns = [
    # Rotas públicas da conta e dos endereços do cliente
    path("enderecos/", views.meus_enderecos, name="meus_enderecos"),
    path("enderecos/novo/", views.meu_endereco_salvar, name="meu_endereco_criar"),
    path("enderecos/<int:pk>/editar/", views.meu_endereco_salvar, name="meu_endereco_editar"),
    path("enderecos/<int:pk>/remover/", views.meu_endereco_desativar, name="meu_endereco_desativar"),
    path(
        "login/",
        views.login_usuario,
        name="login",
    ),

    path(
        "cadastro/",
        views.cadastro_usuario,
        name="cadastro",
    ),

    path(
        "logout/",
        views.logout_usuario,
        name="logout",
    ),
]


# Rotas do gerenciamento de clientes e endereços
management_urlpatterns = [
    path(
        "clientes/",
        views.cliente_lista,
        name="cliente_lista",
    ),
    path(
        "clientes/novo/",
        views.cliente_criar,
        name="cliente_criar",
    ),
    path(
        "clientes/<int:pk>/",
        views.cliente_detalhe,
        name="cliente_detalhe",
    ),
    path(
        "clientes/<int:pk>/editar/",
        views.cliente_editar,
        name="cliente_editar",
    ),
    path(
        "clientes/<int:pk>/excluir/",
        views.cliente_excluir,
        name="cliente_excluir",
    ),
    path(
        "enderecos/",
        views.endereco_lista,
        name="endereco_lista",
    ),
    path(
        "enderecos/novo/",
        views.endereco_criar,
        name="endereco_criar",
    ),
    path(
        "enderecos/<int:pk>/",
        views.endereco_detalhe,
        name="endereco_detalhe",
    ),
    path(
        "enderecos/<int:pk>/editar/",
        views.endereco_editar,
        name="endereco_editar",
    ),
    path(
        "enderecos/<int:pk>/excluir/",
        views.endereco_excluir,
        name="endereco_excluir",
    ),
]
