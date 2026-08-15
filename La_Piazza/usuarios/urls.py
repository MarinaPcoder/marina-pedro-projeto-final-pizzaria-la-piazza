from django.urls import path

from . import views


app_name = "usuarios"


urlpatterns = [
    path(
        "login/",
        views.login_usuario,
        name="login",
    ),

    path(
        "cadastro/",
        views.cadastro_usuario,
        name="cadastro",
    ),

    path(
        "logout/",
        views.logout_usuario,
        name="logout",
    ),
]