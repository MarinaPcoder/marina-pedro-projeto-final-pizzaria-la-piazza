from functools import wraps

from django.contrib import messages
from django.core.exceptions import ValidationError
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect

from .models import Pedido
from .services import garantir_editavel


def pedido_editavel(view):
    @wraps(view)
    def wrapper(request, *args, **kwargs):
        pk = kwargs.get("pedido_pk", kwargs.get("pk"))
        with transaction.atomic():
            pedido = get_object_or_404(Pedido.objects.select_for_update(), pk=pk)
            try:
                garantir_editavel(pedido)
            except ValidationError as erro:
                messages.error(request, " ".join(erro.messages))
                return redirect("pedidos:pedido_detalhe", pk=pk)
            return view(request, *args, **kwargs)
    return wrapper
