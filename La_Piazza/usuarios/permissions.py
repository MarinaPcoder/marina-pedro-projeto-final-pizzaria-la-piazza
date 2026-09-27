from functools import wraps

from django.core.exceptions import PermissionDenied


GRUPO_CLIENTE = "Cliente"
GRUPO_FUNCIONARIO = "Funcionario"


def usuario_eh_funcionario(usuario):
    if not usuario.is_authenticated:
        return False

    return (
        usuario.is_superuser
        or usuario.groups.filter(
            name=GRUPO_FUNCIONARIO
        ).exists()
    )


def funcionario_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if usuario_eh_funcionario(request.user):
            return view_func(request, *args, **kwargs)

        raise PermissionDenied

    return wrapper


def usuario_eh_cliente(usuario):
    return usuario.is_authenticated and usuario.groups.filter(
        name=GRUPO_CLIENTE
    ).exists()


def cliente_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if usuario_eh_cliente(request.user):
            return view_func(request, *args, **kwargs)

        raise PermissionDenied

    return wrapper


PERMISSOES_CLIENTE = [
    "view_categoriapizza",
    "view_pizza",
    "add_pedido",
    "view_pedido",
    "add_itempedido",
    "view_itempedido",
    "add_enderecousuario",
    "change_enderecousuario",
    "delete_enderecousuario",
    "view_enderecousuario",
]

PERMISSOES_FUNCIONARIO = [
    "add_user",
    "change_user",
    "delete_user",
    "view_user",
    "add_usuario",
    "change_usuario",
    "delete_usuario",
    "view_usuario",
    "add_enderecousuario",
    "change_enderecousuario",
    "delete_enderecousuario",
    "view_enderecousuario",
    "add_categoriaestoque",
    "change_categoriaestoque",
    "delete_categoriaestoque",
    "view_categoriaestoque",
    "add_itemestoque",
    "change_itemestoque",
    "delete_itemestoque",
    "view_itemestoque",
    "add_movimentacaoestoque",
    "change_movimentacaoestoque",
    "delete_movimentacaoestoque",
    "view_movimentacaoestoque",
    "add_categoriapizza",
    "change_categoriapizza",
    "delete_categoriapizza",
    "view_categoriapizza",
    "add_pizza",
    "change_pizza",
    "delete_pizza",
    "view_pizza",
    "add_receitapizza",
    "change_receitapizza",
    "delete_receitapizza",
    "view_receitapizza",
    "add_pedido",
    "change_pedido",
    "delete_pedido",
    "view_pedido",
    "add_itempedido",
    "change_itempedido",
    "delete_itempedido",
    "view_itempedido",
]
