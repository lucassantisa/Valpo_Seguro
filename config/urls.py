from django.urls import path, include

# Todas las direcciones las maneja nuestra app "rutas".
urlpatterns = [
    path("", include("rutas.urls")),
]
