from django.contrib import admin
from .models import CategoriaPizza, Ingrediente, Pizza

# Register your models here.

# Secção de registro de Categoria das pizzas
admin.site.register(CategoriaPizza)

# Secção de registro de Ingredientes das pizzas
admin.site.register(Ingrediente)

# Secção de registro de Pizzas
admin.site.register(Pizza)

