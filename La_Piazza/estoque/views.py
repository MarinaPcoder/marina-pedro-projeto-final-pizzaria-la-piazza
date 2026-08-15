from django.contrib import messages
from django.contrib.auth.decorators import (
    login_required,
    permission_required,
)
from django.core.paginator import Paginator
from django.db.models import F, Q
from django.db.models.deletion import ProtectedError
from django.shortcuts import (
    get_object_or_404,
    redirect,
    render,
)

from .forms import CategoriaEstoqueForm, ItemEstoqueForm
from .models import CategoriaEstoque, ItemEstoque


@login_required
@permission_required(
    "estoque.view_categoriaestoque",
    raise_exception=True,
)
def categoria_lista(request):

    busca = request.GET.get(
        "q",
        "",
    ).strip()

    categorias = CategoriaEstoque.objects.all()

    if busca:
        categorias = categorias.filter(
            Q(nome__icontains=busca)
            | Q(descricao__icontains=busca)
        )

    categorias = categorias.order_by("nome")

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
        "estoque/categorias/lista.html",
        context,
    )


@login_required
@permission_required(
    "estoque.view_categoriaestoque",
    raise_exception=True,
)
def categoria_detalhe(request, pk):

    categoria = get_object_or_404(
        CategoriaEstoque,
        pk=pk,
    )

    return render(
        request,
        "estoque/categorias/detalhe.html",
        {
            "categoria": categoria,
        },
    )


@login_required
@permission_required(
    "estoque.add_categoriaestoque",
    raise_exception=True,
)
def categoria_criar(request):

    if request.method == "POST":

        form = CategoriaEstoqueForm(
            request.POST
        )

        if form.is_valid():

            categoria = form.save()

            messages.success(
                request,
                "Categoria de estoque cadastrada com sucesso.",
            )

            return redirect(
                "estoque:categoria_detalhe",
                pk=categoria.pk,
            )

    else:
        form = CategoriaEstoqueForm()

    return render(
        request,
        "estoque/categorias/form.html",
        {
            "form": form,
            "titulo": "Nova categoria de estoque",
        },
    )


@login_required
@permission_required(
    "estoque.change_categoriaestoque",
    raise_exception=True,
)
def categoria_editar(request, pk):

    categoria = get_object_or_404(
        CategoriaEstoque,
        pk=pk,
    )

    if request.method == "POST":

        form = CategoriaEstoqueForm(
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
                "estoque:categoria_detalhe",
                pk=categoria.pk,
            )

    else:

        form = CategoriaEstoqueForm(
            instance=categoria
        )

    return render(
        request,
        "estoque/categorias/form.html",
        {
            "form": form,
            "titulo": "Editar categoria de estoque",
            "categoria": categoria,
        },
    )


@login_required
@permission_required(
    "estoque.delete_categoriaestoque",
    raise_exception=True,
)
def categoria_excluir(request, pk):

    categoria = get_object_or_404(
        CategoriaEstoque,
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
                "estoque:categoria_lista"
            )

        except ProtectedError:

            messages.error(
                request,
                (
                    "Esta categoria possui itens de estoque "
                    "vinculados e não pode ser excluída."
                ),
            )

            return redirect(
                "estoque:categoria_detalhe",
                pk=categoria.pk,
            )

    return render(
        request,
        "estoque/categorias/confirmar_exclusao.html",
        {
            "categoria": categoria,
        },
    )

@login_required
@permission_required(
    "estoque.view_itemestoque",
    raise_exception=True,
)
def item_lista(request):

    busca = request.GET.get(
        "q",
        "",
    ).strip()

    categoria_id = request.GET.get(
        "categoria",
        "",
    )

    status = request.GET.get(
        "status",
        "",
    )

    itens = ItemEstoque.objects.select_related(
        "categoria"
    ).all()

    if busca:
        itens = itens.filter(
            Q(nome__icontains=busca)
            | Q(categoria__nome__icontains=busca)
        )

    if categoria_id:
        itens = itens.filter(
            categoria_id=categoria_id
        )

    if status == "baixo":
        itens = itens.filter(
            quantidade_atual__lte=F("estoque_minimo")
        )

    elif status == "normal":
        itens = itens.filter(
            quantidade_atual__gt=F("estoque_minimo")
        )

    itens = itens.order_by("nome")

    paginator = Paginator(
        itens,
        10,
    )

    pagina = request.GET.get("page")

    page_obj = paginator.get_page(
        pagina
    )

    categorias = CategoriaEstoque.objects.filter(
        ativa=True
    ).order_by("nome")

    context = {
        "page_obj": page_obj,
        "categorias": categorias,
        "busca": busca,
        "categoria_selecionada": categoria_id,
        "status_selecionado": status,
    }

    return render(
        request,
        "estoque/itens/lista.html",
        context,
    )


@login_required
@permission_required(
    "estoque.view_itemestoque",
    raise_exception=True,
)
def item_detalhe(request, pk):

    item = get_object_or_404(
        ItemEstoque.objects.select_related(
            "categoria"
        ),
        pk=pk,
    )

    return render(
        request,
        "estoque/itens/detalhe.html",
        {
            "item": item,
        },
    )


@login_required
@permission_required(
    "estoque.add_itemestoque",
    raise_exception=True,
)
def item_criar(request):

    if request.method == "POST":

        form = ItemEstoqueForm(
            request.POST
        )

        if form.is_valid():

            item = form.save()

            messages.success(
                request,
                "Item de estoque cadastrado com sucesso.",
            )

            return redirect(
                "estoque:item_detalhe",
                pk=item.pk,
            )

    else:

        form = ItemEstoqueForm()

    return render(
        request,
        "estoque/itens/form.html",
        {
            "form": form,
            "titulo": "Novo item de estoque",
        },
    )


@login_required
@permission_required(
    "estoque.change_itemestoque",
    raise_exception=True,
)
def item_editar(request, pk):

    item = get_object_or_404(
        ItemEstoque,
        pk=pk,
    )

    if request.method == "POST":

        form = ItemEstoqueForm(
            request.POST,
            instance=item,
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "Item de estoque atualizado com sucesso.",
            )

            return redirect(
                "estoque:item_detalhe",
                pk=item.pk,
            )

    else:

        form = ItemEstoqueForm(
            instance=item
        )

    return render(
        request,
        "estoque/itens/form.html",
        {
            "form": form,
            "titulo": "Editar item de estoque",
            "item": item,
        },
    )


@login_required
@permission_required(
    "estoque.delete_itemestoque",
    raise_exception=True,
)
def item_excluir(request, pk):

    item = get_object_or_404(
        ItemEstoque,
        pk=pk,
    )

    if request.method == "POST":

        try:

            item.delete()

            messages.success(
                request,
                "Item de estoque excluído com sucesso.",
            )

            return redirect(
                "estoque:item_lista"
            )

        except ProtectedError:

            messages.error(
                request,
                (
                    "Este item está sendo utilizado em receitas "
                    "ou movimentações e não pode ser excluído."
                ),
            )

            return redirect(
                "estoque:item_detalhe",
                pk=item.pk,
            )

    return render(
        request,
        "estoque/itens/confirmar_exclusao.html",
        {
            "item": item,
        },
    )