from django.urls import path

from . import views


app_name = "painel"


urlpatterns = [
    path(
        "",
        views.dashboard,
        name="dashboard",
    ),

    path(
        "dados/",
        views.dashboard_dados,
        name="dados",
    ),
]