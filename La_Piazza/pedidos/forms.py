
from django import forms

from django.db.models import Q
from django.contrib.auth.models import User

from pizza.models import Pizza

from usuarios.permissions import (
    GRUPO_CLIENTE,
    GRUPO_FUNCIONARIO,
)

from .models import (
    ItemPedido,
    Pedido,
)


class PedidoForm(forms.ModelForm):

    class Meta:
        model = Pedido

        fields = [
            "usuario",
            "status",
            "tipo_atendimento",
            "observacoes",
        ]

        widgets = {
            "usuario": forms.Select(
                attrs={
                    "class": "form-control",
                }
            ),

            "status": forms.Select(
                attrs={
                    "class": "form-control",
                }
            ),

            "tipo_atendimento": forms.Select(
                attrs={
                    "class": "form-control",
                }
            ),

            "observacoes": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                    "placeholder": "Observações do pedido",
                }
            ),
        }

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        clientes = (
            User.objects
            .filter(
                groups__name=GRUPO_CLIENTE
            )
            .exclude(
                groups__name=GRUPO_FUNCIONARIO
            )
            .distinct()
            .order_by(
                "first_name",
                "username",
            )
        )

        self.fields["usuario"].queryset = clientes

class ItemPedidoForm(forms.ModelForm):

    class Meta:
        model = ItemPedido

        fields = [
            "pizza",
            "quantidade",
        ]

        widgets = {
            "pizza": forms.Select(
                attrs={
                    "class": "form-control",
                }
            ),

            "quantidade": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": "1",
                    "step": "1",
                    "placeholder": "Ex.: 2",
                }
            ),
        }

    def __init__(
        self,
        *args,
        pedido=None,
        **kwargs,
    ):
        super().__init__(
            *args,
            **kwargs,
        )

        self.pedido = pedido

        pizzas = Pizza.objects.filter(
            disponivel=True
        ).order_by(
            "nome"
        )

        # Se estivermos editando um item cuja pizza
        # foi posteriormente marcada como indisponível,
        # ela continua aparecendo no formulário.
        if self.instance.pk:
            pizzas = Pizza.objects.filter(
                Q(disponivel=True)
                | Q(pk=self.instance.pizza_id)
            ).order_by(
                "nome"
            )

        self.fields["pizza"].queryset = pizzas

    def clean_quantidade(self):

        quantidade = self.cleaned_data[
            "quantidade"
        ]

        if quantidade < 1:
            raise forms.ValidationError(
                "A quantidade deve ser pelo menos 1."
            )

        return quantidade

    def clean_pizza(self):

        pizza = self.cleaned_data[
            "pizza"
        ]

        if self.pedido:

            itens = ItemPedido.objects.filter(
                pedido=self.pedido,
                pizza=pizza,
            )

            if self.instance.pk:
                itens = itens.exclude(
                    pk=self.instance.pk
                )

            if itens.exists():
                raise forms.ValidationError(
                    (
                        "Esta pizza já está no pedido. "
                        "Edite a quantidade do item existente."
                    )
                )

        return pizza
