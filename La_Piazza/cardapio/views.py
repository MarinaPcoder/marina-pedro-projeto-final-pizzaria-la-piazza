from django.shortcuts import render

from .models import CategoriaPizza, Pizza, ReceitaPizza
from .forms import PizzaForm
from django.shortcuts import redirect

# Create your views here.

def index(request):

    caminhotemplate = 'cardapio/index.html'

    context = {
        'categorias': CategoriaPizza.objects.all(),
        'pizzas': Pizza.objects.all(),
        'receitas': ReceitaPizza.objects.all()
    }

    return render(request, caminhotemplate, context)

def menu(request):
    caminhotemplate = 'cardapio/menu.html'

    context = {
        'categorias': CategoriaPizza.objects.all(),
        'pizzas': Pizza.objects.all(),
        'receitas': ReceitaPizza.objects.all()
    }

    return render(request, caminhotemplate, context)

def sobre(request):
    caminhotemplate = 'cardapio/sobre.html'

    return render(request, caminhotemplate)

def CriarPizza(request):
    caminhotemplate = 'produto/form_pizza.html'

    if request.method == "POST":
        form = PizzaForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("menu")  # Redireciona para a página de menu após salvar a pizza
    else:
        form = PizzaForm()

    context = {
        "form": form,
        "titulo": "Cadastrar Pizza",
        "botao": "Cadastrar",
    }
    return render(request, caminhotemplate, context)

def AtualizarPizza(request):
    pass

def DeletarPizza(request):
    pass

