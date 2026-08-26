from django import forms
from django.contrib.auth.forms import (
    AuthenticationForm,
    UserCreationForm,
)
from django.contrib.auth.models import User

from .models import Usuario
from .models import EnderecoUsuario
from .permissions import GRUPO_CLIENTE, GRUPO_FUNCIONARIO


class LoginForm(AuthenticationForm):
    username = forms.CharField(
        label="Usuário",
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Digite seu usuário",
                "autocomplete": "username",
            }
        ),
    )

    password = forms.CharField(
        label="Senha",
        strip=False,
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                "placeholder": "Digite sua senha",
                "autocomplete": "current-password",
            }
        ),
    )


class CadastroUsuarioForm(UserCreationForm):
    telefone = forms.CharField(
        required=False,
        label="Telefone",
    )

    cpf = forms.CharField(
        required=False,
        label="CPF",
    )

    class Meta(UserCreationForm.Meta):
        model = Usuario

        fields = (
            "username",
            "first_name",
            "last_name",
            "email",
            "telefone",
            "cpf",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["first_name"].required = True
        self.fields["last_name"].required = True
        self.fields["email"].required = True

        placeholders = {
            "username": "Escolha um nome de usuário",
            "first_name": "Seu nome",
            "last_name": "Seu sobrenome",
            "email": "seu@email.com",
            "telefone": "(00) 00000-0000",
            "cpf": "000.000.000-00",
            "password1": "Crie uma senha",
            "password2": "Repita sua senha",
        }

        for nome, campo in self.fields.items():
            campo.widget.attrs.update(
                {
                    "class": "form-control",
                    "placeholder": placeholders.get(
                        nome,
                        "",
                    ),
                }
            )

    def clean_email(self):
        email = (
            self.cleaned_data
            .get("email", "")
            .strip()
            .lower()
        )

        if User.objects.filter(
            email__iexact=email
        ).exists():
            raise forms.ValidationError(
                "Já existe uma conta com este e-mail."
            )

        return email

    def clean_cpf(self):
        cpf = self.cleaned_data.get("cpf") or None

        if cpf and Usuario.objects.filter(cpf=cpf).exists():
            raise forms.ValidationError(
                "Já existe uma conta com este CPF."
            )

        return cpf


class ClienteEdicaoForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = (
            "username",
            "first_name",
            "last_name",
            "email",
            "telefone",
            "cpf",
            "observacoes",
            "is_active",
        )
        widgets = {
            "observacoes": forms.Textarea(
                attrs={"rows": 4}
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for campo in self.fields.values():
            if isinstance(
                campo.widget,
                forms.CheckboxInput,
            ):
                campo.widget.attrs["class"] = (
                    "form-check-input"
                )
            else:
                campo.widget.attrs["class"] = (
                    "form-control"
                )

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        usuarios = User.objects.filter(email__iexact=email)

        if self.instance.pk:
            usuarios = usuarios.exclude(pk=self.instance.pk)

        if usuarios.exists():
            raise forms.ValidationError(
                "Já existe uma conta com este e-mail."
            )

        return email

    def clean_cpf(self):
        cpf = self.cleaned_data.get("cpf") or None
        usuarios = Usuario.objects.filter(cpf=cpf)

        if self.instance.pk:
            usuarios = usuarios.exclude(pk=self.instance.pk)

        if cpf and usuarios.exists():
            raise forms.ValidationError(
                "Já existe uma conta com este CPF."
            )

        return cpf


class EnderecoUsuarioForm(forms.ModelForm):
    class Meta:
        model = EnderecoUsuario
        fields = (
            "usuario",
            "logradouro",
            "numero",
            "bairro",
            "cidade",
            "estado",
            "complemento",
            "referencia",
            "principal",
            "ativo",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["usuario"].queryset = (
            Usuario.objects.filter(groups__name=GRUPO_CLIENTE)
            .exclude(groups__name=GRUPO_FUNCIONARIO)
            .distinct()
            .order_by("first_name", "username")
        )

        for campo in self.fields.values():
            if isinstance(
                campo.widget,
                forms.CheckboxInput,
            ):
                campo.widget.attrs["class"] = (
                    "form-check-input"
                )
            else:
                campo.widget.attrs["class"] = (
                    "form-control"
                )
