from django import forms

from .models import CategoriaEstoque, ItemEstoque


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

        if self.instance.pk:
            categorias = categorias.exclude(
                pk=self.instance.pk
            )

        if categorias.exists():
            raise forms.ValidationError(
                "Já existe uma categoria de estoque com esse nome."
            )

        return nome


class ItemEstoqueForm(forms.ModelForm):

    class Meta:
        model = ItemEstoque

        fields = [
            "categoria",
            "nome",
            "unidade_medida",
            "quantidade_atual",
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

            "quantidade_atual": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "step": "0.001",
                    "min": "0",
                    "placeholder": "Ex.: 15.500",
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

        if self.instance.pk:
            itens = itens.exclude(
                pk=self.instance.pk
            )

        if itens.exists():
            raise forms.ValidationError(
                "Já existe um item de estoque com esse nome."
            )

        return nome

    def clean_quantidade_atual(self):
        quantidade = self.cleaned_data["quantidade_atual"]

        if quantidade < 0:
            raise forms.ValidationError(
                "A quantidade não pode ser negativa."
            )

        return quantidade

    def clean_estoque_minimo(self):
        estoque_minimo = self.cleaned_data["estoque_minimo"]

        if estoque_minimo < 0:
            raise forms.ValidationError(
                "O estoque mínimo não pode ser negativo."
            )

        return estoque_minimo

    def clean_preco_custo(self):
        preco = self.cleaned_data["preco_custo"]

        if preco < 0:
            raise forms.ValidationError(
                "O preço de custo não pode ser negativo."
            )

        return preco