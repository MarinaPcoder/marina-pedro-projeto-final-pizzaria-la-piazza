from django.test import TestCase

from .models import EnderecoUsuario, Usuario


class UsuarioTests(TestCase):
    def test_usuario_guarda_dados_do_projeto(self):
        usuario = Usuario.objects.create_user(
            username="cliente",
            password="senha-teste",
            telefone="71999999999",
            cpf="12345678901",
        )

        self.assertEqual(usuario.telefone, "71999999999")
        self.assertEqual(usuario.cpf, "12345678901")

    def test_usuario_pode_ter_varios_enderecos(self):
        usuario = Usuario.objects.create_user(
            username="cliente",
            password="senha-teste",
        )

        EnderecoUsuario.objects.create(
            usuario=usuario,
            logradouro="Rua A",
            numero="10",
            bairro="Centro",
            cidade="Salvador",
            estado="BA",
            principal=True,
        )
        EnderecoUsuario.objects.create(
            usuario=usuario,
            logradouro="Rua B",
            numero="20",
            bairro="Brotas",
            cidade="Salvador",
            estado="BA",
        )

        self.assertEqual(usuario.enderecos.count(), 2)
