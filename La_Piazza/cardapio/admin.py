from django.contrib import admin
from .models import CategoriaPizza, Pizza, ReceitaPizza

# Register your models here.

# Secção de registro de Categoria das pizzas
admin.site.register(CategoriaPizza)

# Secção de registro de Pizzas
admin.site.register(Pizza)

# Secção de registro das receitas das pizzas
admin.site.register(ReceitaPizza)
