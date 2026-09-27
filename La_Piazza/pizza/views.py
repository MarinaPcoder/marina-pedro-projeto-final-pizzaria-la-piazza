from django.contrib import messages
from django.conf import settings
from django.contrib.auth.decorators import (
    login_required,
    permission_required,
)

from django.core.paginator import Paginator
from django.db.models import Q, Sum
from django.db.models.deletion import ProtectedError
from django.shortcuts import (
    get_object_or_404,
    redirect,
    render,
)

# Forms
from .forms import (
    CategoriaPizzaForm,
    PizzaForm,
    ReceitaPizzaForm,
)

# Modelos
from .models import (
    CategoriaPizza,
    Pizza,
    ReceitaPizza,
)

from usuarios.permissions import funcionario_required
from pedidos.models import ItemPedido, STATUS_PEDIDO_ENTREGUE


# Views de páginas públicas
def index(request):
    pizzas_disponiveis = Pizza.objects.filter(disponivel=True, categoria__ativa=True)
    mais_vendidas_ids = list(
        ItemPedido.objects.filter(
            pedido__status=STATUS_PEDIDO_ENTREGUE,
            pizza__disponivel=True,
            pizza__categoria__ativa=True,
        )
        .values("pizza_id")
        .annotate(total_vendido=Sum("quantidade"))
        .order_by("-total_vendido", "pizza_id")
        .values_list("pizza_id", flat=True)[:2]
    )
    pizzas_por_id = Pizza.objects.in_bulk(mais_vendidas_ids)
    destaques_carrossel = [pizzas_por_id[pk] for pk in mais_vendidas_ids]
    if len(destaques_carrossel) < 2:
        destaques_carrossel.extend(
            pizzas_disponiveis.exclude(pk__in=mais_vendidas_ids).order_by("nome")[:2 - len(destaques_carrossel)]
        )

    context = {
        "categorias": CategoriaPizza.objects.filter(ativa=True),
        "pizzas": pizzas_disponiveis,
        "destaques_carrossel": destaques_carrossel,
        "mais_vendidas_ids": mais_vendidas_ids,
        "google_maps_api_key": settings.GOOGLE_MAPS_API_KEY,
    }

    return render(
        request,
        "pizza/index.html",
        context,
    )


def menu(request):
    pizzas = Pizza.objects.filter(disponivel=True, categoria__ativa=True).select_related("categoria")
    categoria = request.GET.get("categoria", "")
    if categoria.isdigit():
        pizzas = pizzas.filter(categoria_id=categoria)
    context = {
        "categorias": CategoriaPizza.objects.filter(ativa=True),
        "pizzas": pizzas,
        "categoria_selecionada": categoria,
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
        {"google_maps_api_key": settings.GOOGLE_MAPS_API_KEY},
    )


# CRUD de categorias de pizza
# Read - List - Categorias
@login_required
@funcionario_required
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


# Read - Detail - Categorias
@login_required
@funcionario_required
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


# Create - Categorias
@login_required
@funcionario_required
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


# Update - Categorias
@login_required
@funcionario_required
@permission_required(
    "cardapio.change_categoriapizza",
    raise_exception=True,
)
def categoria_editar(request, pk):

    categoria = get_object_or_404(
        CategoriaPizza,
        pk=pk,
    )

    categoria = CategoriaPizza.objects.get(
        pk=pk
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


# Delete - Categorias
@login_required
@funcionario_required
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


# CRUD de pizzas
# Read - List - Pizzas
@login_required
@funcionario_required
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

# Read - Detail - Pizzas
@login_required
@funcionario_required
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

# Create - Pizzas
@login_required
@funcionario_required
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

# Update - Pizzas
@login_required
@funcionario_required
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

# Delete - Pizzas
@login_required
@funcionario_required
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


# CRUD de receitas de pizza
# Read - List - Receitas
@login_required
@funcionario_required
@permission_required(
    "cardapio.view_receitapizza",
    raise_exception=True,
)
def receita_geral_lista(request):
    busca = request.GET.get("q", "").strip()

    receitas = ReceitaPizza.objects.select_related(
        "pizza",
        "item_estoque",
    )

    if busca:
        receitas = receitas.filter(
            Q(pizza__nome__icontains=busca)
            | Q(item_estoque__nome__icontains=busca)
        )

    page_obj = Paginator(
        receitas.order_by(
            "pizza__nome",
            "item_estoque__nome",
        ),
        15,
    ).get_page(request.GET.get("page"))

    return render(
        request,
        "pizza/receitas/lista_geral.html",
        {
            "page_obj": page_obj,
            "busca": busca,
        },
    )

# Read - List - Receitas de uma pizza específica
@login_required
@funcionario_required
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

# Create - Receitas
@login_required
@funcionario_required
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

# Update - Receitas
@login_required
@funcionario_required
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

# Delete - Receitas
@login_required
@funcionario_required
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
