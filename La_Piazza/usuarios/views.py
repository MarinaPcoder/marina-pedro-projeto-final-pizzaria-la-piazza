from functools import wraps

from django.core.exceptions import PermissionDenied
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import (
    login_required,
    permission_required,
)
from django.contrib.auth.models import Group
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Q
from django.db.models.deletion import ProtectedError
from django.shortcuts import (
    get_object_or_404,
    redirect,
    render,
)
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST

# Forms
from .forms import (
    CadastroUsuarioForm,
    ClienteEdicaoForm,
    EnderecoUsuarioForm,
    LoginForm,
    MeuEnderecoForm,
)

# Modelos
from .models import EnderecoUsuario, Usuario


# Permissões e grupos: identificação de perfis e controle de acesso
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


# Gerenciamento interno: clientes e endereços
# CRUD de clientes
# Read - List - Clientes
@login_required
@funcionario_required
@permission_required(
    "usuarios.view_usuario",
    raise_exception=True,
)
def cliente_lista(request):
    busca = request.GET.get("q", "").strip()
    clientes = _clientes().order_by("first_name", "username")

    if busca:
        clientes = clientes.filter(
            Q(username__icontains=busca)
            | Q(first_name__icontains=busca)
            | Q(last_name__icontains=busca)
            | Q(email__icontains=busca)
            | Q(cpf__icontains=busca)
        )

    page_obj = Paginator(clientes, 12).get_page(
        request.GET.get("page")
    )

    return render(
        request,
        "usuarios/gerenciamento/clientes/lista.html",
        {
            "page_obj": page_obj,
            "busca": busca,
        },
    )


# Read - Detail - Clientes
@login_required
@funcionario_required
@permission_required(
    "usuarios.view_usuario",
    raise_exception=True,
)
def cliente_detalhe(request, pk):
    cliente = get_object_or_404(_clientes(), pk=pk)

    return render(
        request,
        "usuarios/gerenciamento/clientes/detalhe.html",
        {
            "cliente": cliente,
            "enderecos": cliente.enderecos.order_by(
                "-principal",
                "logradouro",
            ),
        },
    )


# Create - Clientes
@login_required
@funcionario_required
@permission_required(
    "usuarios.add_usuario",
    raise_exception=True,
)
def cliente_criar(request):
    form = CadastroUsuarioForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        cliente = form.save()
        grupo_cliente, _ = Group.objects.get_or_create(
            name=GRUPO_CLIENTE
        )
        cliente.groups.add(grupo_cliente)

        messages.success(
            request,
            "Cliente cadastrado com sucesso.",
        )
        return redirect(
            "usuarios_gerenciamento:cliente_detalhe",
            pk=cliente.pk,
        )

    return render(
        request,
        "usuarios/gerenciamento/clientes/form.html",
        {
            "form": form,
            "titulo": "Novo cliente",
        },
    )


# Update - Clientes
@login_required
@funcionario_required
@permission_required(
    "usuarios.change_usuario",
    raise_exception=True,
)
def cliente_editar(request, pk):
    cliente = get_object_or_404(_clientes(), pk=pk)
    form = ClienteEdicaoForm(
        request.POST or None,
        instance=cliente,
    )

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(
            request,
            "Cliente atualizado com sucesso.",
        )
        return redirect(
            "usuarios_gerenciamento:cliente_detalhe",
            pk=cliente.pk,
        )

    return render(
        request,
        "usuarios/gerenciamento/clientes/form.html",
        {
            "form": form,
            "titulo": "Editar cliente",
            "cliente": cliente,
        },
    )


# Delete - Clientes
@login_required
@funcionario_required
@permission_required(
    "usuarios.delete_usuario",
    raise_exception=True,
)
def cliente_excluir(request, pk):
    cliente = get_object_or_404(_clientes(), pk=pk)

    if request.method == "POST":
        try:
            cliente.delete()
        except ProtectedError:
            messages.error(
                request,
                "Este cliente possui pedidos e não pode ser excluído.",
            )
            return redirect(
                "usuarios_gerenciamento:cliente_detalhe",
                pk=cliente.pk,
            )

        messages.success(
            request,
            "Cliente excluído com sucesso.",
        )
        return redirect(
            "usuarios_gerenciamento:cliente_lista"
        )

    return render(
        request,
        "usuarios/gerenciamento/clientes/confirmar_exclusao.html",
        {"cliente": cliente},
    )


# CRUD de endereços
# Read - List - Endereços
@login_required
@funcionario_required
@permission_required(
    "usuarios.view_enderecousuario",
    raise_exception=True,
)
def endereco_lista(request):
    busca = request.GET.get("q", "").strip()
    enderecos = EnderecoUsuario.objects.select_related(
        "usuario"
    )

    if busca:
        enderecos = enderecos.filter(
            Q(usuario__username__icontains=busca)
            | Q(usuario__first_name__icontains=busca)
            | Q(usuario__last_name__icontains=busca)
            | Q(logradouro__icontains=busca)
            | Q(bairro__icontains=busca)
            | Q(cidade__icontains=busca)
        )

    page_obj = Paginator(
        enderecos.order_by(
            "usuario__first_name",
            "usuario__username",
            "-principal",
        ),
        15,
    ).get_page(request.GET.get("page"))

    return render(
        request,
        "usuarios/gerenciamento/enderecos/lista.html",
        {
            "page_obj": page_obj,
            "busca": busca,
        },
    )


# Read - Detail - Endereços
@login_required
@funcionario_required
@permission_required(
    "usuarios.view_enderecousuario",
    raise_exception=True,
)
def endereco_detalhe(request, pk):
    endereco = get_object_or_404(
        EnderecoUsuario.objects.select_related("usuario"),
        pk=pk,
    )

    return render(
        request,
        "usuarios/gerenciamento/enderecos/detalhe.html",
        {"endereco": endereco},
    )


# Create - Endereços
@login_required
@funcionario_required
@permission_required(
    "usuarios.add_enderecousuario",
    raise_exception=True,
)
def endereco_criar(request):
    initial = {}
    cliente_id = request.GET.get("cliente")

    if cliente_id:
        initial["usuario"] = get_object_or_404(
            _clientes(),
            pk=cliente_id,
        )

    form = EnderecoUsuarioForm(
        request.POST or None,
        initial=initial,
    )

    if request.method == "POST" and form.is_valid():
        endereco = _salvar_endereco(form)
        messages.success(
            request,
            "Endereço cadastrado com sucesso.",
        )
        return redirect(
            "usuarios_gerenciamento:endereco_detalhe",
            pk=endereco.pk,
        )

    return render(
        request,
        "usuarios/gerenciamento/enderecos/form.html",
        {
            "form": form,
            "titulo": "Novo endereço",
        },
    )


# Update - Endereços
@login_required
@funcionario_required
@permission_required(
    "usuarios.change_enderecousuario",
    raise_exception=True,
)
def endereco_editar(request, pk):
    endereco = get_object_or_404(EnderecoUsuario, pk=pk)
    form = EnderecoUsuarioForm(
        request.POST or None,
        instance=endereco,
    )

    if request.method == "POST" and form.is_valid():
        endereco = _salvar_endereco(form)
        messages.success(
            request,
            "Endereço atualizado com sucesso.",
        )
        return redirect(
            "usuarios_gerenciamento:endereco_detalhe",
            pk=endereco.pk,
        )

    return render(
        request,
        "usuarios/gerenciamento/enderecos/form.html",
        {
            "form": form,
            "titulo": "Editar endereço",
            "endereco": endereco,
        },
    )


# Delete - Endereços
@login_required
@funcionario_required
@permission_required(
    "usuarios.delete_enderecousuario",
    raise_exception=True,
)
def endereco_excluir(request, pk):
    endereco = get_object_or_404(
        EnderecoUsuario.objects.select_related("usuario"),
        pk=pk,
    )

    if request.method == "POST":
        cliente_pk = endereco.usuario_id
        endereco.delete()
        messages.success(
            request,
            "Endereço excluído com sucesso.",
        )
        return redirect(
            "usuarios_gerenciamento:cliente_detalhe",
            pk=cliente_pk,
        )

    return render(
        request,
        "usuarios/gerenciamento/enderecos/confirmar_exclusao.html",
        {"endereco": endereco},
    )


# Site público: autenticação de usuários
# Login
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


# Cadastro
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


# Logout
@login_required
@require_POST
def logout_usuario(request):
    logout(request)

    messages.success(
        request,
        "Você saiu da sua conta.",
    )

    return redirect("index")


# Endereços do cliente no site público
@login_required
@cliente_required
def meus_enderecos(request):
    return render(request, "usuarios/enderecos.html", {"enderecos": request.user.enderecos.filter(ativo=True)})


@login_required
@cliente_required
@transaction.atomic
def meu_endereco_salvar(request, pk=None):
    User.objects.select_for_update().get(pk=request.user.pk)
    voltar_checkout = request.GET.get("voltar") == "checkout"
    endereco = get_object_or_404(EnderecoUsuario, pk=pk, usuario=request.user, ativo=True) if pk else None
    form = MeuEnderecoForm(request.POST if request.method == "POST" else None, instance=endereco)
    if request.method == "POST" and form.is_valid():
        endereco = form.save(commit=False)
        endereco.usuario = request.user
        if endereco.principal:
            request.user.enderecos.exclude(pk=endereco.pk).update(principal=False)
        endereco.save()
        messages.success(request, "Endereco salvo.")
        return redirect("compras:checkout" if voltar_checkout else "usuarios:meus_enderecos")
    return render(request, "usuarios/endereco_form.html", {"form": form, "endereco": endereco, "voltar_checkout": voltar_checkout})


@login_required
@cliente_required
@require_POST
def meu_endereco_desativar(request, pk):
    endereco = get_object_or_404(EnderecoUsuario, pk=pk, usuario=request.user, ativo=True)
    endereco.ativo = False
    endereco.principal = False
    endereco.save(update_fields=["ativo", "principal", "atualizado_em"])
    messages.success(request, "Endereco removido dos seus enderecos ativos.")
    return redirect("usuarios:meus_enderecos")


# Funções auxiliares de clientes
def _clientes():
    return (
        Usuario.objects.filter(groups__name=GRUPO_CLIENTE)
        .distinct()
    )


# Função auxiliar para salvar endereços
def _salvar_endereco(form):
    endereco = form.save()

    if endereco.principal:
        EnderecoUsuario.objects.filter(
            usuario=endereco.usuario,
        ).exclude(pk=endereco.pk).update(principal=False)

    return endereco


# Contexto dos templates: perfis do usuário e seção ativa do gerenciamento
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
