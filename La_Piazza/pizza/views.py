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

from .forms import (
    CategoriaPizzaForm,
    PizzaForm,
    ReceitaPizzaForm,
)

from .models import (
    CategoriaPizza,
    Pizza,
    ReceitaPizza,
)

def index(request):
    context = {
        "categorias": CategoriaPizza.objects.all(),
        "pizzas": Pizza.objects.all(),
    }

    return render(
        request,
        "pizza/index.html",
        context,
    )


def menu(request):
    context = {
        "categorias": CategoriaPizza.objects.all(),
        "pizzas": Pizza.objects.all(),
    }

    return render(
        request,
        "pizza/menu.html",
        context,
    )


def sobre(request):
    return render(
        request,
        "pizza/sobre.html",
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
        "pizza/categorias/lista.html",
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
        "pizza/categorias/detalhe.html",
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
        "pizza/categorias/form.html",
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
        "pizza/categorias/form.html",
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
        "pizza/categorias/confirmar_exclusao.html",
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
        "pizza/pizzas/lista.html",
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
        "pizza/pizzas/detalhe.html",
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
        "pizza/pizzas/form.html",
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
        "pizza/pizzas/form.html",
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
        "pizza/pizzas/confirmar_exclusao.html",
        {
            "pizza": pizza,
        },
    )

@login_required
@permission_required(
    "cardapio.view_receitapizza",
    raise_exception=True,
)
def receita_lista(request, pizza_pk):

    pizza = get_object_or_404(
        Pizza,
        pk=pizza_pk,
    )

    receita = (
        ReceitaPizza.objects
        .filter(
            pizza=pizza
        )
        .select_related(
            "item_estoque"
        )
        .order_by(
            "item_estoque__nome"
        )
    )

    return render(
        request,
        "pizza/receitas/lista.html",
        {
            "pizza": pizza,
            "receita": receita,
        },
    )


@login_required
@permission_required(
    "cardapio.add_receitapizza",
    raise_exception=True,
)
def receita_adicionar(request, pizza_pk):

    pizza = get_object_or_404(
        Pizza,
        pk=pizza_pk,
    )

    if request.method == "POST":

        form = ReceitaPizzaForm(
            request.POST,
            pizza=pizza,
        )

        if form.is_valid():

            ingrediente = form.save(
                commit=False
            )

            ingrediente.pizza = pizza

            ingrediente.save()

            messages.success(
                request,
                "Ingrediente adicionado à receita.",
            )

            return redirect(
                "receita_lista",
                pizza_pk=pizza.pk,
            )

    else:

        form = ReceitaPizzaForm(
            pizza=pizza
        )

    return render(
        request,
        "pizza/receitas/form.html",
        {
            "form": form,
            "pizza": pizza,
            "titulo": (
                f"Adicionar ingrediente — {pizza.nome}"
            ),
        },
    )


@login_required
@permission_required(
    "cardapio.change_receitapizza",
    raise_exception=True,
)
def receita_editar(
    request,
    pizza_pk,
    receita_pk,
):

    pizza = get_object_or_404(
        Pizza,
        pk=pizza_pk,
    )

    ingrediente = get_object_or_404(
        ReceitaPizza,
        pk=receita_pk,
        pizza=pizza,
    )

    if request.method == "POST":

        form = ReceitaPizzaForm(
            request.POST,
            instance=ingrediente,
            pizza=pizza,
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "Ingrediente atualizado.",
            )

            return redirect(
                "receita_lista",
                pizza_pk=pizza.pk,
            )

    else:

        form = ReceitaPizzaForm(
            instance=ingrediente,
            pizza=pizza,
        )

    return render(
        request,
        "pizza/receitas/form.html",
        {
            "form": form,
            "pizza": pizza,
            "ingrediente": ingrediente,
            "titulo": (
                f"Editar ingrediente — {pizza.nome}"
            ),
        },
    )


@login_required
@permission_required(
    "cardapio.delete_receitapizza",
    raise_exception=True,
)
def receita_excluir(
    request,
    pizza_pk,
    receita_pk,
):

    pizza = get_object_or_404(
        Pizza,
        pk=pizza_pk,
    )

    ingrediente = get_object_or_404(
        ReceitaPizza,
        pk=receita_pk,
        pizza=pizza,
    )

    if request.method == "POST":

        ingrediente.delete()

        messages.success(
            request,
            "Ingrediente removido da receita.",
        )

        return redirect(
            "receita_lista",
            pizza_pk=pizza.pk,
        )

    return render(
        request,
        "pizza/receitas/confirmar_exclusao.html",
        {
            "pizza": pizza,
            "ingrediente": ingrediente,
        },
    )
