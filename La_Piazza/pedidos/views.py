from uuid import UUID, uuid4

from django.core.exceptions import ValidationError
from django.views.decorators.http import require_POST

from django.contrib import messages
from django.contrib.auth.decorators import (
    login_required,
    permission_required,
)
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Q
from django.shortcuts import (
    get_object_or_404,
    redirect,
    render,
)

from pizza.models import Pizza
from usuarios.permissions import cliente_required, funcionario_required

# Forms
from .forms import CheckoutForm, ItemPedidoForm, PedidoForm, QuantidadeForm
from .cart import CART_KEY, itens_carrinho, salvar_carrinho, total_carrinho
from .decorators import pedido_editavel
from .services import alterar_status, confirmar_pedido, proximos_status

# Modelos
from .models import (
    ItemPedido,
    Pedido,
    STATUS_PEDIDO_CHOICES,
    STATUS_PEDIDO_PENDENTE,
    TIPO_ATENDIMENTO_CHOICES,
)


# Gerenciamento de pedidos e itens
# CRUD de pedidos
# Read - List - Pedidos
@login_required
@funcionario_required
@permission_required(
    "pedidos.view_pedido",
    raise_exception=True,
)
def pedido_lista(request):

    busca = request.GET.get(
        "q",
        "",
    ).strip()

    status = request.GET.get(
        "status",
        "",
    )

    tipo = request.GET.get(
        "tipo",
        "",
    )

    pedidos = (
        Pedido.objects
        .select_related(
            "usuario",
            "endereco_entrega",
        )
        .prefetch_related(
            "itens"
        )
    )

    if busca:

        filtro = (
            Q(
                usuario__username__icontains=busca
            )
            | Q(
                usuario__first_name__icontains=busca
            )
            | Q(
                usuario__last_name__icontains=busca
            )
        )

        if busca.isdigit():
            filtro |= Q(
                pk=int(busca)
            )

        pedidos = pedidos.filter(
            filtro
        )

    if status:
        pedidos = pedidos.filter(
            status=status
        )

    if tipo:
        pedidos = pedidos.filter(
            tipo_atendimento=tipo
        )

    paginator = Paginator(
        pedidos,
        10,
    )

    pagina = request.GET.get(
        "page"
    )

    page_obj = paginator.get_page(
        pagina
    )

    context = {
        "page_obj": page_obj,
        "busca": busca,
        "status_selecionado": status,
        "tipo_selecionado": tipo,
        "status_opcoes": STATUS_PEDIDO_CHOICES,
        "tipo_opcoes": TIPO_ATENDIMENTO_CHOICES,
    }

    return render(
        request,
        "pedidos/lista.html",
        context,
    )


# Read - Detail - Pedidos
@login_required
@funcionario_required
@permission_required(
    "pedidos.view_pedido",
    raise_exception=True,
)
def pedido_detalhe(request, pk):

    pedido = get_object_or_404(
        Pedido.objects
        .select_related(
            "usuario",
            "endereco_entrega",
        )
        .prefetch_related(
            "itens__pizza"
        ),
        pk=pk,
    )

    return render(
        request,
        "pedidos/detalhe.html",
        {
            "pedido": pedido,
            "proximos_status": [(valor, dict(STATUS_PEDIDO_CHOICES)[valor]) for valor in proximos_status(pedido)],
        },
    )


# Create - Pedidos
@login_required
@funcionario_required
@permission_required(
    "pedidos.add_pedido",
    raise_exception=True,
)
def pedido_criar(request):

    if request.method == "POST":

        form = PedidoForm(
            request.POST
        )

        if form.is_valid():

            pedido = form.save(commit=False)
            pedido.registrado_por = request.user
            pedido.origem = "BALCAO"
            pedido.status = STATUS_PEDIDO_PENDENTE
            pedido.endereco_entrega_texto = Pedido.texto_endereco(
                pedido.endereco_entrega
            )
            pedido.full_clean()
            pedido.save()

            messages.success(
                request,
                "Pedido cadastrado com sucesso.",
            )

            return redirect(
                "pedidos:pedido_detalhe",
                pk=pedido.pk,
            )

    else:

        form = PedidoForm()

    return render(
        request,
        "pedidos/form.html",
        {
            "form": form,
            "titulo": "Novo pedido",
        },
    )


# Update - Pedidos
@login_required
@funcionario_required
@permission_required(
    "pedidos.change_pedido",
    raise_exception=True,
)
@pedido_editavel
def pedido_editar(request, pk):

    pedido = get_object_or_404(
        Pedido,
        pk=pk,
    )

    if request.method == "POST":

        form = PedidoForm(
            request.POST,
            instance=pedido,
        )

        if form.is_valid():

            pedido = form.save(commit=False)
            if "endereco_entrega" in form.changed_data:
                pedido.endereco_entrega_texto = Pedido.texto_endereco(
                    pedido.endereco_entrega
                )
            pedido.save()

            messages.success(
                request,
                "Pedido atualizado com sucesso.",
            )

            return redirect(
                "pedidos:pedido_detalhe",
                pk=pedido.pk,
            )

    else:

        form = PedidoForm(
            instance=pedido
        )

    return render(
        request,
        "pedidos/form.html",
        {
            "form": form,
            "titulo": f"Editar Pedido #{pedido.pk}",
            "pedido": pedido,
        },
    )


# Delete - Pedidos
@login_required
@funcionario_required
@permission_required(
    "pedidos.delete_pedido",
    raise_exception=True,
)
@pedido_editavel
def pedido_excluir(request, pk):

    pedido = get_object_or_404(
        Pedido,
        pk=pk,
    )

    if request.method == "POST":

        pedido.delete()

        messages.success(
            request,
            "Pedido excluído com sucesso.",
        )

        return redirect(
            "pedidos:pedido_lista"
        )

    return render(
        request,
        "pedidos/confirmar_exclusao.html",
        {
            "pedido": pedido,
        },
    )


# CRUD de itens do pedido
# Read - List - Itens
@login_required
@funcionario_required
@permission_required(
    "pedidos.view_itempedido",
    raise_exception=True,
)
def item_lista(request):
    busca = request.GET.get("q", "").strip()

    itens = ItemPedido.objects.select_related(
        "pedido",
        "pedido__usuario",
        "pizza",
    )

    if busca:
        filtro = (
            Q(pizza__nome__icontains=busca)
            | Q(pedido__usuario__username__icontains=busca)
            | Q(pedido__usuario__first_name__icontains=busca)
            | Q(pedido__usuario__last_name__icontains=busca)
        )

        if busca.isdigit():
            filtro |= Q(pedido_id=int(busca))

        itens = itens.filter(filtro)

    page_obj = Paginator(
        itens.order_by("-pedido__criado_em", "pizza__nome"),
        15,
    ).get_page(request.GET.get("page"))

    return render(
        request,
        "pedidos/itens/lista.html",
        {
            "page_obj": page_obj,
            "busca": busca,
        },
    )


# Create - Itens
@login_required
@funcionario_required
@permission_required(
    "pedidos.add_itempedido",
    raise_exception=True,
)
@pedido_editavel
def item_adicionar(request, pedido_pk):

    pedido = get_object_or_404(
        Pedido,
        pk=pedido_pk,
    )

    if request.method == "POST":

        form = ItemPedidoForm(
            request.POST,
            pedido=pedido,
        )

        if form.is_valid():

            item = form.save(
                commit=False
            )

            item.pedido = pedido

            item.save()

            messages.success(
                request,
                "Pizza adicionada ao pedido.",
            )

            return redirect(
                "pedidos:pedido_detalhe",
                pk=pedido.pk,
            )

    else:

        form = ItemPedidoForm(
            pedido=pedido
        )

    return render(
        request,
        "pedidos/itens/form.html",
        {
            "form": form,
            "pedido": pedido,
            "titulo": (
                f"Adicionar pizza ao Pedido #{pedido.pk}"
            ),
        },
    )


# Update - Itens
@login_required
@funcionario_required
@permission_required(
    "pedidos.change_itempedido",
    raise_exception=True,
)
@pedido_editavel
def item_editar(request, pedido_pk, item_pk):

    pedido = get_object_or_404(
        Pedido,
        pk=pedido_pk,
    )

    item = get_object_or_404(
        ItemPedido,
        pk=item_pk,
        pedido=pedido,
    )

    if request.method == "POST":

        form = ItemPedidoForm(
            request.POST,
            instance=item,
            pedido=pedido,
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "Item atualizado com sucesso.",
            )

            return redirect(
                "pedidos:pedido_detalhe",
                pk=pedido.pk,
            )

    else:

        form = ItemPedidoForm(
            instance=item,
            pedido=pedido,
        )

    return render(
        request,
        "pedidos/itens/form.html",
        {
            "form": form,
            "pedido": pedido,
            "item": item,
            "titulo": (
                f"Editar item do Pedido #{pedido.pk}"
            ),
        },
    )


# Delete - Itens
@login_required
@funcionario_required
@permission_required(
    "pedidos.delete_itempedido",
    raise_exception=True,
)
@pedido_editavel
def item_excluir(request, pedido_pk, item_pk):

    pedido = get_object_or_404(
        Pedido,
        pk=pedido_pk,
    )

    item = get_object_or_404(
        ItemPedido,
        pk=item_pk,
        pedido=pedido,
    )

    if request.method == "POST":

        pizza_nome = item.pizza.nome

        item.delete()

        messages.success(
            request,
            (
                f"{pizza_nome} removida "
                "do pedido."
            ),
        )

        return redirect(
            "pedidos:pedido_detalhe",
            pk=pedido.pk,
        )

    return render(
        request,
        "pedidos/itens/confirmar_exclusao.html",
        {
            "pedido": pedido,
            "item": item,
        },
    )


# Confirmação de pedidos
@login_required
@funcionario_required
@permission_required(
    "pedidos.change_pedido",
    raise_exception=True,
)
@permission_required(
    "estoque.add_movimentacaoestoque",
    raise_exception=True,
)
@require_POST
def pedido_confirmar(request, pk):

    pedido = get_object_or_404(
        Pedido,
        pk=pk,
    )

    if not pedido.itens.exists():

        messages.error(
            request,
            "Não é possível confirmar um pedido sem pizzas.",
        )

        return redirect(
            "pedidos:pedido_detalhe",
            pk=pedido.pk,
        )

    try:

        confirmar_pedido(pedido.pk, responsavel=request.user)

    except ValidationError as erro:

        messages.error(
            request,
            " ".join(erro.messages),
        )

        return redirect(
            "pedidos:pedido_detalhe",
            pk=pedido.pk,
        )

    except ValueError as erro:

        messages.error(
            request,
            str(erro),
        )

        return redirect(
            "pedidos:pedido_detalhe",
            pk=pedido.pk,
        )

    messages.success(
        request,
        (
            "Pedido confirmado e estoque "
            "baixado com sucesso."
        ),
    )

    return redirect(
        "pedidos:pedido_detalhe",
        pk=pedido.pk,
    )


@login_required
@funcionario_required
@permission_required("pedidos.change_pedido", raise_exception=True)
@require_POST
def pedido_status(request, pk):
    get_object_or_404(Pedido, pk=pk)
    try:
        alterar_status(pk, request.POST.get("status"))
        messages.success(request, "Status atualizado.")
    except ValidationError as erro:
        messages.error(request, " ".join(erro.messages))
    return redirect("pedidos:pedido_detalhe", pk=pk)


# Compra pública: carrinho, checkout e acompanhamento do cliente
def carrinho(request):
    itens = itens_carrinho(request.session)
    return render(request, "pedidos/publico/carrinho.html", {
        "itens": itens, "total": total_carrinho(itens),
    })


@require_POST
def carrinho_adicionar(request, pizza_pk):
    pizza = get_object_or_404(Pizza, pk=pizza_pk, disponivel=True, categoria__ativa=True)
    form = QuantidadeForm(request.POST)
    if form.is_valid():
        dados = request.session.get(CART_KEY, {})
        quantidade = dados.get(str(pizza.pk), {}).get("quantidade", 0) + form.cleaned_data["quantidade"]
        if quantidade <= 99:
            dados[str(pizza.pk)] = {"quantidade": quantidade, "preco": str(pizza.preco)}
            salvar_carrinho(request.session, dados)
            messages.success(request, "Pizza adicionada ao carrinho.")
        else:
            messages.error(request, "Limite de 99 unidades por pizza.")
    else:
        messages.error(request, "Informe uma quantidade inteira entre 1 e 99.")
    return redirect("compras:carrinho")


@require_POST
def carrinho_atualizar(request, pizza_pk):
    dados = request.session.get(CART_KEY, {})
    chave = str(pizza_pk)
    if chave not in dados:
        return redirect("compras:carrinho")
    if request.POST.get("remover") == "1":
        del dados[chave]
        salvar_carrinho(request.session, dados)
    else:
        form = QuantidadeForm(request.POST)
        if form.is_valid():
            dados[chave]["quantidade"] = form.cleaned_data["quantidade"]
            salvar_carrinho(request.session, dados)
        else:
            messages.error(request, "Informe uma quantidade inteira entre 1 e 99.")
    return redirect("compras:carrinho")


@login_required
@cliente_required
def checkout(request):
    # A chave persistida torna o reenvio do mesmo checkout idempotente.
    try:
        token_recebido = UUID(request.POST.get("checkout_token", ""))
    except (ValueError, TypeError):
        token_recebido = None
    if request.method == "POST" and token_recebido:
        existente = Pedido.objects.filter(checkout_token=token_recebido, usuario=request.user).first()
        if existente:
            return redirect("compras:detalhe", pk=existente.pk)
    itens = itens_carrinho(request.session)
    if not itens:
        messages.error(request, "Seu carrinho esta vazio.")
        return redirect("compras:carrinho")
    token = request.session.get("checkout_token") or str(uuid4())
    request.session["checkout_token"] = token
    form = CheckoutForm(
        request.POST if request.method == "POST" else None, usuario=request.user,
        initial={"checkout_token": token, "endereco_entrega": request.user.enderecos.filter(ativo=True, principal=True).first()},
    )
    if request.method == "POST" and form.is_valid():
        if str(form.cleaned_data["checkout_token"]) != token:
            form.add_error(None, "O carrinho mudou. Atualize a pagina antes de enviar.")
        else:
            try:
                with transaction.atomic():
                    User.objects.select_for_update().get(pk=request.user.pk)
                    existente = Pedido.objects.filter(checkout_token=token, usuario=request.user).first()
                    if existente:
                        return redirect("compras:detalhe", pk=existente.pk)
                    dados = request.session[CART_KEY]
                    pizzas = {str(p.pk): p for p in Pizza.objects.select_for_update().filter(pk__in=dados).select_related("categoria")}
                    if len(pizzas) != len(dados) or any(not p.disponivel or not p.categoria.ativa for p in pizzas.values()):
                        raise ValidationError("Ha pizzas indisponiveis. Revise o carrinho.")
                    if any(str(p.preco) != dados[chave]["preco"] for chave, p in pizzas.items()):
                        for chave, pizza in pizzas.items():
                            dados[chave]["preco"] = str(pizza.preco)
                        request.session[CART_KEY] = dados
                        raise ValidationError("Os precos mudaram. Confira o novo total e envie novamente.")
                    endereco = form.cleaned_data["endereco_entrega"]
                    if endereco:
                        endereco = request.user.enderecos.select_for_update().filter(pk=endereco.pk, ativo=True).first()
                        if not endereco:
                            raise ValidationError("O endereco nao esta mais disponivel.")
                    pedido = Pedido(
                        usuario=request.user, registrado_por=None, origem="SITE", checkout_token=token,
                        tipo_atendimento=form.cleaned_data["tipo_atendimento"], endereco_entrega=endereco,
                        endereco_entrega_texto=Pedido.texto_endereco(endereco),
                        observacoes=form.cleaned_data["observacoes"],
                    )
                    pedido.full_clean()
                    pedido.save()
                    for chave, pizza in pizzas.items():
                        ItemPedido.objects.create(pedido=pedido, pizza=pizza, quantidade=dados[chave]["quantidade"], preco_unitario=pizza.preco)
                salvar_carrinho(request.session, {})
                messages.success(request, "Pedido enviado. Aguarde a confirmacao da pizzaria.")
                return redirect("compras:detalhe", pk=pedido.pk)
            except ValidationError as erro:
                form.add_error(None, " ".join(erro.messages))
                itens = itens_carrinho(request.session)
    return render(request, "pedidos/publico/checkout.html", {"form": form, "itens": itens, "total": total_carrinho(itens)})


@login_required
@cliente_required
def meus_pedidos(request):
    pedidos = Pedido.objects.filter(usuario=request.user).prefetch_related("itens")
    return render(request, "pedidos/publico/lista.html", {"page_obj": Paginator(pedidos, 10).get_page(request.GET.get("page"))})


@login_required
@cliente_required
def detalhe(request, pk):
    pedido = get_object_or_404(Pedido.objects.prefetch_related("itens__pizza"), pk=pk, usuario=request.user)
    return render(request, "pedidos/publico/detalhe.html", {"pedido": pedido})


@login_required
@cliente_required
@require_POST
def cancelar(request, pk):
    get_object_or_404(Pedido, pk=pk, usuario=request.user)
    try:
        alterar_status(pk, "CANCELADO", usuario=request.user)
        messages.success(request, "Pedido cancelado.")
    except ValidationError as erro:
        messages.error(request, " ".join(erro.messages))
    return redirect("compras:detalhe", pk=pk)
