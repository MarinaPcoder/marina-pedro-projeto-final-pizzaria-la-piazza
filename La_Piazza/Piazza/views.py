from django.shortcuts import render


# Páginas de erro
# Erro 403 - Acesso negado
def erro_403(
    request,
    exception=None,
):

    return render(
        request,
        "erros/403.html",
        status=403,
    )


# Erro 404 - Página não encontrada
def erro_404(
    request,
    exception=None,
):

    return render(
        request,
        "erros/404.html",
        status=404,
    )
