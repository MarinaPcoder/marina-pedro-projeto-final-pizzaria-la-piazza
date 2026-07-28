from django.contrib import admin
from .models import ItemEstoque, MovimentacaoEstoque, CategoriaEstoque

# Register your models here.

# Registro de item no estoque no painel administrativo do Django
admin.site.register(ItemEstoque)

# Registro de movimentação no estoque no painel administrativo do Django
admin.site.register(MovimentacaoEstoque)

# Registro de categoria no estoque no painel administrativo do Django
admin.site.register(CategoriaEstoque)