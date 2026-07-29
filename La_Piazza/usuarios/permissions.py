GRUPO_CLIENTE = "Cliente"
GRUPO_FUNCIONARIO = "Funcionario"

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


def criar_grupos_e_permissoes(sender, **kwargs):
    Group = sender.apps.get_model("auth", "Group")
    Permission = sender.apps.get_model("auth", "Permission")

    cliente, _ = Group.objects.get_or_create(name=GRUPO_CLIENTE)
    funcionario, _ = Group.objects.get_or_create(name=GRUPO_FUNCIONARIO)

    cliente.permissions.set(
        Permission.objects.filter(codename__in=PERMISSOES_CLIENTE)
    )
    funcionario.permissions.set(
        Permission.objects.filter(codename__in=PERMISSOES_FUNCIONARIO)
    )
