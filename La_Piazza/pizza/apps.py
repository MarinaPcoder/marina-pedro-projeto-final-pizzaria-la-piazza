from django.apps import AppConfig


class PizzaConfig(AppConfig):
    name = "pizza"
    verbose_name = "pizzas"
    # Mantém o app_label antigo para preservar tabelas, permissões e
    # dependências das migrações já aplicadas.
    label = "cardapio"
