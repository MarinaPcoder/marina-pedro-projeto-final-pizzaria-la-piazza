from django.core.exceptions import ValidationError
from django.db import transaction
from django.views.decorators.http import require_POST

from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import (
    get_object_or_404,
    redirect,
    render,
)

from .forms import ItemPedidoForm, PedidoForm
from .models import (
    ItemPedido,
    Pedido,
    STATUS_PEDIDO_CHOICES,
    STATUS_PEDIDO_CONFIRMADO,
    TIPO_ATENDIMENTO_CHOICES,
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
        },
    )


def pedido_criar(request):

    if request.method == "POST":

        form = PedidoForm(
            request.POST
        )

        if form.is_valid():

            pedido = form.save()

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

            form.save()

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

        with transaction.atomic():

            pedido.baixar_estoque(
                responsavel=request.user
            )

            pedido.status = STATUS_PEDIDO_CONFIRMADO

            pedido.save(
                update_fields=[
                    "status",
                    "atualizado_em",
                ]
            )

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
