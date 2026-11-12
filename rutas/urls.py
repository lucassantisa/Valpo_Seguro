from django.urls import path

from . import views

urlpatterns = [
    path("", views.mapa, name="mapa"),
    path("lugares/", views.lugares, name="lugares"),
    path("registro/", views.registro, name="registro"),
    path("ingresar/", views.iniciar_sesion, name="login"),
    path("salir/", views.salir, name="salir"),
]
