from django.shortcuts import render

# Create your views here.

from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from django.shortcuts import redirect, render
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST

from .forms import CadastroUsuarioForm, LoginForm
from .permissions import GRUPO_CLIENTE


def login_usuario(request):
    if request.user.is_authenticated:
        return redirect("index")

    form = LoginForm(
        request=request,
        data=request.POST or None,
    )

    if request.method == "POST" and form.is_valid():
        usuario = form.get_user()

        login(
            request,
            usuario,
        )

        messages.success(
            request,
            "Login realizado com sucesso.",
        )

        proxima_pagina = (
            request.POST.get("next")
            or request.GET.get("next")
        )

        if (
            proxima_pagina
            and url_has_allowed_host_and_scheme(
                url=proxima_pagina,
                allowed_hosts={
                    request.get_host()
                },
                require_https=request.is_secure(),
            )
        ):
            return redirect(proxima_pagina)

        return redirect("index")

    context = {
        "form": form,
        "next": request.GET.get(
            "next",
            "",
        ),
    }

    return render(
        request,
        "usuarios/login.html",
        context,
    )


def cadastro_usuario(request):
    if request.user.is_authenticated:
        return redirect("index")

    if request.method == "POST":
        form = CadastroUsuarioForm(
            request.POST
        )

        if form.is_valid():
            usuario = form.save()

            grupo_cliente, _ = (
                Group.objects.get_or_create(
                    name=GRUPO_CLIENTE
                )
            )

            usuario.groups.add(
                grupo_cliente
            )

            login(
                request,
                usuario,
            )

            messages.success(
                request,
                "Sua conta foi criada com sucesso.",
            )

            return redirect("index")

    else:
        form = CadastroUsuarioForm()

    return render(
        request,
        "usuarios/cadastro.html",
        {
            "form": form,
        },
    )


@login_required
@require_POST
def logout_usuario(request):
    logout(request)

    messages.success(
        request,
        "Você saiu da sua conta.",
    )

    return redirect("index")
