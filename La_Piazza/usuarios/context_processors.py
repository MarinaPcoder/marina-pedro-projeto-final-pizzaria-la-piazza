from .permissions import usuario_eh_cliente, usuario_eh_funcionario


def acesso_administrativo(request):
    resolver = getattr(request, "resolver_match", None)
    namespace = resolver.namespace if resolver else ""
    url_name = resolver.url_name if resolver else ""

    if namespace == "estoque":
        secao_gerencia = "estoque"
    elif namespace == "pedidos":
        secao_gerencia = "pedido"
    elif namespace == "usuarios_gerenciamento":
        secao_gerencia = "usuario"
    elif url_name in {
        "categoria_lista",
        "categoria_detalhe",
        "categoria_criar",
        "categoria_editar",
        "categoria_excluir",
        "pizza_lista",
        "pizza_detalhe",
        "pizza_criar",
        "pizza_editar",
        "pizza_excluir",
        "receita_lista",
        "receita_geral_lista",
        "receita_adicionar",
        "receita_editar",
        "receita_excluir",
    }:
        secao_gerencia = "pizza"
    else:
        secao_gerencia = ""

    return {
        "eh_funcionario": usuario_eh_funcionario(
            request.user
        ),
        "eh_cliente": usuario_eh_cliente(request.user),
        "secao_gerencia": secao_gerencia,
    }
