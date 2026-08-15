from django import forms

from .models import (
    CategoriaEstoque,
    ItemEstoque,
    MovimentacaoEstoque,
)


# =========================================================
# FORMULÁRIO - CATEGORIA DE ESTOQUE
# =========================================================

class CategoriaEstoqueForm(forms.ModelForm):

    class Meta:
        model = CategoriaEstoque

        fields = [
            "nome",
            "descricao",
            "ativa",
        ]

        widgets = {
            "nome": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Ex.: Ingredientes",
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

        categorias = CategoriaEstoque.objects.filter(
            nome__iexact=nome
        )

        # Na edição, ignora a própria categoria.
        if self.instance.pk:
            categorias = categorias.exclude(
                pk=self.instance.pk
            )

        if categorias.exists():
            raise forms.ValidationError(
                "Já existe uma categoria de estoque com esse nome."
            )

        return nome


# =========================================================
# FORMULÁRIO - ITEM DE ESTOQUE
# =========================================================

class ItemEstoqueForm(forms.ModelForm):

    class Meta:
        model = ItemEstoque

        fields = [
            "categoria",
            "nome",
            "unidade_medida",
            "estoque_minimo",
            "preco_custo",
            "data_validade",
            "ativo",
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
                    "placeholder": "Ex.: Mussarela",
                }
            ),

            "unidade_medida": forms.Select(
                attrs={
                    "class": "form-control",
                }
            ),

            "estoque_minimo": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "step": "0.001",
                    "min": "0",
                    "placeholder": "Ex.: 5.000",
                }
            ),

            "preco_custo": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "step": "0.01",
                    "min": "0",
                    "placeholder": "Ex.: 32.90",
                }
            ),

            "data_validade": forms.DateInput(
                attrs={
                    "class": "form-control",
                    "type": "date",
                }
            ),

            "ativo": forms.CheckboxInput(
                attrs={
                    "class": "form-check-input",
                }
            ),
        }

    def clean_nome(self):
        nome = self.cleaned_data["nome"].strip()

        itens = ItemEstoque.objects.filter(
            nome__iexact=nome
        )

        # Na edição, ignora o próprio item.
        if self.instance.pk:
            itens = itens.exclude(
                pk=self.instance.pk
            )

        if itens.exists():
            raise forms.ValidationError(
                "Já existe um item de estoque com esse nome."
            )

        return nome

    def clean_estoque_minimo(self):
        estoque_minimo = self.cleaned_data[
            "estoque_minimo"
        ]

        if estoque_minimo < 0:
            raise forms.ValidationError(
                "O estoque mínimo não pode ser negativo."
            )

        return estoque_minimo

    def clean_preco_custo(self):
        preco = self.cleaned_data[
            "preco_custo"
        ]

        if preco < 0:
            raise forms.ValidationError(
                "O preço de custo não pode ser negativo."
            )

        return preco


# =========================================================
# FORMULÁRIO - MOVIMENTAÇÃO DE ESTOQUE
# =========================================================

class MovimentacaoEstoqueForm(forms.ModelForm):

    class Meta:
        model = MovimentacaoEstoque

        fields = [
            "item",
            "tipo",
            "quantidade",
            "motivo",
        ]

        widgets = {
            "item": forms.Select(
                attrs={
                    "class": "form-control",
                }
            ),

            "tipo": forms.Select(
                attrs={
                    "class": "form-control",
                }
            ),

            "quantidade": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "step": "0.001",
                    "min": "0.001",
                    "placeholder": "Ex.: 5.000",
                }
            ),

            "motivo": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": (
                        "Ex.: Compra de fornecedor, "
                        "produto vencido, correção de inventário..."
                    ),
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(
            *args,
            **kwargs
        )

        # Apenas itens ativos podem receber movimentações.
        self.fields["item"].queryset = (
            ItemEstoque.objects
            .filter(ativo=True)
            .order_by("nome")
        )

    def clean_quantidade(self):
        quantidade = self.cleaned_data[
            "quantidade"
        ]

        if quantidade <= 0:
            raise forms.ValidationError(
                "A quantidade deve ser maior que zero."
            )

        return quantidade