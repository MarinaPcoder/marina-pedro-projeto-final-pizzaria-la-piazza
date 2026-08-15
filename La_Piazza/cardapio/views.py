from django.contrib import messages
from django.contrib.auth.decorators import (
    login_required,
    permission_required,
)
from django.core.paginator import Paginator
from django.db.models import Q
from django.db.models.deletion import ProtectedError
from django.shortcuts import (
    get_object_or_404,
    redirect,
    render,
)

from .forms import CategoriaPizzaForm, PizzaForm
from .models import CategoriaPizza, Pizza


def index(request):
    context = {
        "categorias": CategoriaPizza.objects.all(),
        "pizzas": Pizza.objects.all(),
    }

    return render(
        request,
        "cardapio/index.html",
        context,
    )


def menu(request):
    context = {
        "categorias": CategoriaPizza.objects.all(),
        "pizzas": Pizza.objects.all(),
    }

    return render(
        request,
        "cardapio/menu.html",
        context,
    )


def sobre(request):
    return render(
        request,
        "cardapio/sobre.html",
    )


@login_required
@permission_required(
    "cardapio.view_categoriapizza",
    raise_exception=True,
)
def categoria_lista(request):

    busca = request.GET.get(
        "q",
        "",
    ).strip()

    categorias = CategoriaPizza.objects.all()

    if busca:
        categorias = categorias.filter(
            Q(nome__icontains=busca)
            | Q(descricao__icontains=busca)
        )

    paginator = Paginator(
        categorias,
        10,
    )

    pagina = request.GET.get("page")

    page_obj = paginator.get_page(
        pagina
    )

    context = {
        "page_obj": page_obj,
        "busca": busca,
    }

    return render(
        request,
        "cardapio/categorias/lista.html",
        context,
    )


@login_required
@permission_required(
    "cardapio.view_categoriapizza",
    raise_exception=True,
)
def categoria_detalhe(request, pk):

    categoria = get_object_or_404(
        CategoriaPizza,
        pk=pk,
    )

    return render(
        request,
        "cardapio/categorias/detalhe.html",
        {
            "categoria": categoria,
        },
    )


@login_required
@permission_required(
    "cardapio.add_categoriapizza",
    raise_exception=True,
)
def categoria_criar(request):

    if request.method == "POST":

        form = CategoriaPizzaForm(
            request.POST
        )

        if form.is_valid():

            categoria = form.save()

            messages.success(
                request,
                "Categoria cadastrada com sucesso.",
            )

            return redirect(
                "categoria_detalhe",
                pk=categoria.pk,
            )

    else:
        form = CategoriaPizzaForm()

    return render(
        request,
        "cardapio/categorias/form.html",
        {
            "form": form,
            "titulo": "Nova categoria",
        },
    )


@login_required
@permission_required(
    "cardapio.change_categoriapizza",
    raise_exception=True,
)
def categoria_editar(request, pk):

    categoria = get_object_or_404(
        CategoriaPizza,
        pk=pk,
    )

    if request.method == "POST":

        form = CategoriaPizzaForm(
            request.POST,
            instance=categoria,
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "Categoria atualizada com sucesso.",
            )

            return redirect(
                "categoria_detalhe",
                pk=categoria.pk,
            )

    else:
        form = CategoriaPizzaForm(
            instance=categoria
        )

    return render(
        request,
        "cardapio/categorias/form.html",
        {
            "form": form,
            "titulo": "Editar categoria",
        },
    )


@login_required
@permission_required(
    "cardapio.delete_categoriapizza",
    raise_exception=True,
)
def categoria_excluir(request, pk):

    categoria = get_object_or_404(
        CategoriaPizza,
        pk=pk,
    )

    if request.method == "POST":

        try:
            categoria.delete()

            messages.success(
                request,
                "Categoria excluída com sucesso.",
            )

            return redirect(
                "categoria_lista"
            )

        except ProtectedError:

            messages.error(
                request,
                (
                    "Essa categoria possui pizzas "
                    "cadastradas e não pode ser excluída."
                ),
            )

            return redirect(
                "categoria_detalhe",
                pk=categoria.pk,
            )

    return render(
        request,
        "cardapio/categorias/confirmar_exclusao.html",
        {
            "categoria": categoria,
        },
    )

@login_required
@permission_required(
    "cardapio.view_pizza",
    raise_exception=True,
)
def pizza_lista(request):

    busca = request.GET.get(
        "q",
        "",
    ).strip()

    categoria_id = request.GET.get(
        "categoria",
        "",
    )

    pizzas = Pizza.objects.select_related(
        "categoria"
    ).all()

    if busca:
        pizzas = pizzas.filter(
            Q(nome__icontains=busca)
            | Q(descricao__icontains=busca)
            | Q(categoria__nome__icontains=busca)
        )

    if categoria_id:
        pizzas = pizzas.filter(
            categoria_id=categoria_id
        )

    pizzas = pizzas.order_by("nome")

    paginator = Paginator(
        pizzas,
        10,
    )

    pagina = request.GET.get("page")

    page_obj = paginator.get_page(
        pagina
    )

    categorias = CategoriaPizza.objects.filter(
        ativa=True
    ).order_by("nome")

    context = {
        "page_obj": page_obj,
        "categorias": categorias,
        "busca": busca,
        "categoria_selecionada": categoria_id,
    }

    return render(
        request,
        "cardapio/pizzas/lista.html",
        context,
    )


@login_required
@permission_required(
    "cardapio.view_pizza",
    raise_exception=True,
)
def pizza_detalhe(request, pk):

    pizza = get_object_or_404(
        Pizza.objects.select_related(
            "categoria"
        ),
        pk=pk,
    )

    return render(
        request,
        "cardapio/pizzas/detalhe.html",
        {
            "pizza": pizza,
        },
    )


@login_required
@permission_required(
    "cardapio.add_pizza",
    raise_exception=True,
)
def pizza_criar(request):

    if request.method == "POST":

        form = PizzaForm(
            request.POST,
            request.FILES,
        )

        if form.is_valid():

            pizza = form.save()

            messages.success(
                request,
                "Pizza cadastrada com sucesso.",
            )

            return redirect(
                "pizza_detalhe",
                pk=pizza.pk,
            )

    else:
        form = PizzaForm()

    return render(
        request,
        "cardapio/pizzas/form.html",
        {
            "form": form,
            "titulo": "Nova pizza",
        },
    )


@login_required
@permission_required(
    "cardapio.change_pizza",
    raise_exception=True,
)
def pizza_editar(request, pk):

    pizza = get_object_or_404(
        Pizza,
        pk=pk,
    )

    if request.method == "POST":

        form = PizzaForm(
            request.POST,
            request.FILES,
            instance=pizza,
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "Pizza atualizada com sucesso.",
            )

            return redirect(
                "pizza_detalhe",
                pk=pizza.pk,
            )

    else:
        form = PizzaForm(
            instance=pizza
        )

    return render(
        request,
        "cardapio/pizzas/form.html",
        {
            "form": form,
            "titulo": "Editar pizza",
            "pizza": pizza,
        },
    )


@login_required
@permission_required(
    "cardapio.delete_pizza",
    raise_exception=True,
)
def pizza_excluir(request, pk):

    pizza = get_object_or_404(
        Pizza,
        pk=pk,
    )

    if request.method == "POST":

        try:
            pizza.delete()

            messages.success(
                request,
                "Pizza excluída com sucesso.",
            )

            return redirect(
                "pizza_lista"
            )

        except ProtectedError:

            messages.error(
                request,
                (
                    "Esta pizza já está relacionada "
                    "a pedidos e não pode ser excluída."
                ),
            )

            return redirect(
                "pizza_detalhe",
                pk=pizza.pk,
            )

    return render(
        request,
        "cardapio/pizzas/confirmar_exclusao.html",
        {
            "pizza": pizza,
        },
    )