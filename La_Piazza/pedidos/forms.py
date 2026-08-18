
from django import forms

from django.db.models import Q
from django.contrib.auth.models import User

from pizza.models import Pizza

from usuarios.models import EnderecoUsuario
from usuarios.permissions import (
    GRUPO_CLIENTE,
    GRUPO_FUNCIONARIO,
)

from .models import (
    ItemPedido,
    Pedido,
    TIPO_ATENDIMENTO_ENTREGA,
    TIPO_ATENDIMENTO_RETIRADA,
)


class EnderecoEntregaChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, endereco):
        usuario = (
            endereco.usuario.get_full_name()
            or endereco.usuario.username
        )

        return f"{usuario} — {endereco}"


class PedidoForm(forms.ModelForm):

    endereco_entrega = EnderecoEntregaChoiceField(
        queryset=EnderecoUsuario.objects.none(),
        required=False,
        widget=forms.Select(
            attrs={
                "class": "form-control",
            }
        ),
        label="Endereço de entrega",
    )

    class Meta:
        model = Pedido

        fields = [
            "usuario",
            "status",
            "tipo_atendimento",
            "endereco_entrega",
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

        self.fields["endereco_entrega"].queryset = (
            EnderecoUsuario.objects
            .filter(
                ativo=True
            )
            .select_related(
                "usuario"
            )
            .order_by(
                "usuario__username",
                "-principal",
                "logradouro",
            )
        )

    def clean(self):

        cleaned_data = super().clean()

        usuario = cleaned_data.get(
            "usuario"
        )

        tipo_atendimento = cleaned_data.get(
            "tipo_atendimento"
        )

        endereco = cleaned_data.get(
            "endereco_entrega"
        )

        if (
            tipo_atendimento
            == TIPO_ATENDIMENTO_ENTREGA
            and not endereco
        ):
            self.add_error(
                "endereco_entrega",
                "Informe o endereço para pedidos de entrega.",
            )

        if (
            usuario
            and endereco
            and endereco.usuario_id != usuario.id
        ):
            self.add_error(
                "endereco_entrega",
                "Este endereço não pertence ao cliente selecionado.",
            )

        if (
            tipo_atendimento
            == TIPO_ATENDIMENTO_RETIRADA
        ):
            cleaned_data["endereco_entrega"] = None

        return cleaned_data

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
