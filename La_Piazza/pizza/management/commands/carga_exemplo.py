from decimal import Decimal

from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from estoque.models import CategoriaEstoque, ItemEstoque, MovimentacaoEstoque
from pizza.models import CategoriaPizza, Pizza, ReceitaPizza


class Command(BaseCommand):
    help = "Cria grupos, categorias, ingredientes e pizzas de exemplo sem sobrescrever dados existentes."

    @transaction.atomic
    def handle(self, *args, **options):
        call_command("configurar_grupos", stdout=self.stdout)
        categoria, _ = CategoriaPizza.objects.get_or_create(nome="Tradicionais")
        ingredientes, _ = CategoriaEstoque.objects.get_or_create(nome="Ingredientes")
        itens = {}
        for nome, unidade, saldo in (("Disco de massa", "UN", "50"), ("Molho de tomate", "KG", "10"), ("Mussarela", "KG", "10"), ("Calabresa", "KG", "5")):
            item, criado = ItemEstoque.objects.get_or_create(nome=nome, defaults={
                "categoria": ingredientes, "unidade_medida": unidade,
                "quantidade_atual": Decimal(saldo), "estoque_minimo": Decimal("2"),
            })
            itens[nome] = item
            if item.unidade_medida != unidade:
                raise CommandError(f"{nome} ja existe com outra unidade. Revise o cadastro antes da carga.")
            if criado:
                MovimentacaoEstoque.objects.create(item=item, tipo="ENTRADA", quantidade=Decimal(saldo), motivo="Saldo inicial de demonstracao")
        base = {"Disco de massa": "1", "Molho de tomate": "0.100", "Mussarela": "0.200"}
        for nome, preco, receita in (("Mussarela", "35.00", base), ("Calabresa", "40.00", {**base, "Calabresa": "0.150"})):
            pizza, criada = Pizza.objects.get_or_create(nome=nome, defaults={
                "categoria": categoria, "preco": Decimal(preco),
                "descricao": ", ".join(receita),
            })
            if criada:
                for ingrediente, quantidade in receita.items():
                    ReceitaPizza.objects.create(pizza=pizza, item_estoque=itens[ingrediente], quantidade_utilizada=Decimal(quantidade))
        self.stdout.write(self.style.SUCCESS("Dados de exemplo criados; cadastros e saldos existentes preservados."))
