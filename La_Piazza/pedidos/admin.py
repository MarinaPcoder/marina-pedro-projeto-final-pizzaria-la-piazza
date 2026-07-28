from django.contrib import admin
from .models import Pedido, ItemPedido

# Register your models here.

# Registro de pedidos no painel administrativo do Django
admin.site.register(Pedido)
# Registro de itens de pedidos no painel administrativo do Django
admin.site.register(ItemPedido)