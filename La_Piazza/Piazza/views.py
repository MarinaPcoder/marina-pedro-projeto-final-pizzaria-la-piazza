from django.shortcuts import render


def erro_403(
    request,
    exception=None,
):

    return render(
        request,
        "erros/403.html",
        status=403,
    )


def erro_404(
    request,
    exception=None,
):

    return render(
        request,
        "erros/404.html",
        status=404,
    )