from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from pedidos.urls import compras_urlpatterns
from usuarios.urls import management_urlpatterns

from . import views

admin.site.site_header = "La Piazza"
admin.site.site_title = "Administração La Piazza"
admin.site.index_title = "Gerenciamento da Pizzaria"


urlpatterns = [
    path("compras/", include((compras_urlpatterns, "compras"), namespace="compras")),
    # Página de Administração
    path(
        "admin/",
        admin.site.urls,
    ),

    # Página Inicial (index)
    path(
        "",
        include("pizza.urls"),
    ),

    # Página de Cadastro e Login
    path(
        "conta/",
        include("usuarios.urls"),
    ),

    # Página de Gerenciamento de Estoque
    path(
        "gerenciamento/estoque/",
        include("estoque.urls"),
    ),

    path(
        "gerenciamento/pedidos/",
        include("pedidos.urls"),
    ),

    # Página de Gerenciamento de Usuários
    path(
        "gerenciamento/usuarios/",
        include((management_urlpatterns, "usuarios_gerenciamento")),
    ),

    # Painel de gerenciamento
    path(
        "painel/",
        views.dashboard,
        name="dashboard",
    ),

    path(
        "painel/dados/",
        views.dashboard_dados,
        name="dashboard_dados",
    ),

]

handler403 = "Piazza.views.erro_403"
handler404 = "Piazza.views.erro_404"

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT,
    )
