from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path


admin.site.site_header = "La Piazza"
admin.site.site_title = "Administração La Piazza"
admin.site.index_title = "Gerenciamento da Pizzaria"


urlpatterns = [
    path(
        "admin/",
        admin.site.urls,
    ),

    path(
        "",
        include("pizza.urls"),
    ),

    path(
        "conta/",
        include("usuarios.urls"),
    ),

    path(
    "gerenciamento/estoque/",
    include("estoque.urls"),
    ),

    path(
    "gerenciamento/pedidos/",
    include("pedidos.urls"),
    ),

    path(
    "painel/",
    include("painel.urls"),
    ),

]

handler403 = "Piazza.views.erro_403"
handler404 = "Piazza.views.erro_404"

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT,
    )
