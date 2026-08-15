from django import forms

from .models import CategoriaPizza, Pizza


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