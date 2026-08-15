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
        include("cardapio.urls"),
    ),

    path(
        "conta/",
        include("usuarios.urls"),
    ),
]


if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT,
    )