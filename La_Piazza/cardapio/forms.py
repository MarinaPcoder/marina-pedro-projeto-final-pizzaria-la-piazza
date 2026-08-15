from django import forms

from .models import CategoriaPizza, Pizza, ReceitaPizza
from estoque.models import ItemEstoque

class CategoriaPizzaForm(forms.ModelForm):

    class Meta:
        model = CategoriaPizza

        fields = [
            "nome",
            "descricao",
            "ativa",
        ]

        widgets = {
            "nome": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Ex.: Tradicional",
                }
            ),
            "descricao": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                    "placeholder": "Descrição da categoria",
                }
            ),
            "ativa": forms.CheckboxInput(
                attrs={
                    "class": "form-check-input",
                }
            ),
        }

    def clean_nome(self):
        nome = self.cleaned_data["nome"].strip()

        categorias = CategoriaPizza.objects.filter(
            nome__iexact=nome
        )

        if self.instance.pk:
            categorias = categorias.exclude(
                pk=self.instance.pk
            )

        if categorias.exists():
            raise forms.ValidationError(
                "Já existe uma categoria com esse nome."
            )

        return nome


class PizzaForm(forms.ModelForm):

    class Meta:
        model = Pizza

        fields = [
            "categoria",
            "nome",
            "descricao",
            "preco",
            "imagem",
            "disponivel",
        ]

        widgets = {
            "categoria": forms.Select(
                attrs={
                    "class": "form-control",
                }
            ),

            "nome": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Ex.: Calabresa",
                }
            ),

            "descricao": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                    "placeholder": "Descrição da pizza",
                }
            ),

            "preco": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "step": "0.01",
                    "min": "0.01",
                    "placeholder": "Ex.: 49.90",
                }
            ),

            "imagem": forms.ClearableFileInput(
                attrs={
                    "class": "form-control",
                    "accept": "image/*",
                }
            ),

            "disponivel": forms.CheckboxInput(
                attrs={
                    "class": "form-check-input",
                }
            ),
        }

    def clean_nome(self):
        nome = self.cleaned_data["nome"].strip()

        pizzas = Pizza.objects.filter(
            nome__iexact=nome
        )

        if self.instance.pk:
            pizzas = pizzas.exclude(
                pk=self.instance.pk
            )

        if pizzas.exists():
            raise forms.ValidationError(
                "Já existe uma pizza com esse nome."
            )

        return nome

class ItemEstoqueChoiceField(forms.ModelChoiceField):

    def label_from_instance(self, item):

        return (
            f"{item.nome} "
            f"({item.get_unidade_medida_display()})"
        )


class ReceitaPizzaForm(forms.ModelForm):

    item_estoque = ItemEstoqueChoiceField(
        queryset=ItemEstoque.objects.none(),
        label="Ingrediente",
        widget=forms.Select(
            attrs={
                "class": "form-control",
            }
        ),
    )

    class Meta:
        model = ReceitaPizza

        fields = [
            "item_estoque",
            "quantidade_utilizada",
        ]

        widgets = {
            "quantidade_utilizada": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "step": "0.001",
                    "min": "0.001",
                    "placeholder": "Ex.: 0.300",
                }
            ),
        }

        labels = {
            "quantidade_utilizada": "Quantidade utilizada",
        }

    def __init__(
        self,
        *args,
        pizza=None,
        **kwargs,
    ):

        super().__init__(
            *args,
            **kwargs,
        )

        self.pizza = pizza

        itens = ItemEstoque.objects.filter(
            ativo=True
        ).order_by(
            "nome"
        )

        if pizza:

            ingredientes_usados = ReceitaPizza.objects.filter(
                pizza=pizza
            )

            if self.instance.pk:

                ingredientes_usados = ingredientes_usados.exclude(
                    pk=self.instance.pk
                )

            itens = itens.exclude(
                pk__in=ingredientes_usados.values(
                    "item_estoque_id"
                )
            )

        self.fields[
            "item_estoque"
        ].queryset = itens

    def clean_quantidade_utilizada(self):

        quantidade = self.cleaned_data[
            "quantidade_utilizada"
        ]

        if quantidade <= 0:

            raise forms.ValidationError(
                "A quantidade precisa ser maior que zero."
            )

        return quantidade