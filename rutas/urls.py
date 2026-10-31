from django.urls import path

from . import views

urlpatterns = [
    path("", views.mapa, name="mapa"),
    path("lugares/", views.lugares, name="lugares"),
]
