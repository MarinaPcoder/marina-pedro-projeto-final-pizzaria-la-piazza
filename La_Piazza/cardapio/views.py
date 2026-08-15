from django.shortcuts import render

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