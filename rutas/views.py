from django.conf import settings
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.shortcuts import redirect, render

from . import calculos, datos
from .models import Resena


def buscar_lugar(id_lugar):
    """Busca un lugar por su id. Devuelve None si no existe."""
    for lugar in datos.LUGARES:
        if lugar["id"] == id_lugar:
            return lugar
    return None


def calcular_resultado(lat, lng, destino_id):
    """Funcionalidad corazón. Entrada: punto de partida y destino. Salida: (resultado, error)."""
    destino = buscar_lugar(destino_id)
    if lat == "" or lng == "":
        return None, "Primero elige tu punto de partida."
    if destino is None:
        return None, "Primero elige un destino."
    try:
        origen = [float(lat), float(lng)]
    except ValueError:
        return None, "El punto de partida no es válido."

    # Procesamiento: pedir rutas (con clave, evitando las zonas) y elegir la que pase menos por zonas
    rutas, error, proveedor, evitando = calculos.buscar_rutas(
        origen, [destino["lat"], destino["lng"]], datos.ZONAS, settings.ORS_API_KEY)
    if error != "":
        return None, error
    ruta = calculos.elegir_ruta(rutas, datos.ZONAS)

    zonas_cruzadas = []
    for nombre, metros in ruta["zonas"].items():
        zonas_cruzadas.append({"nombre": nombre, "metros": max(10, round(metros, -1))})

    resultado = {
        "destino": destino,
        "distancia": round(ruta["distancia"]),
        "minutos": max(1, round(ruta["duracion"] / 60)),
        "zonas_cruzadas": zonas_cruzadas,
        "proveedor": proveedor,
        "evitando": evitando,
        "coordenadas": ruta["coordenadas"],
    }
    return resultado, ""


def mapa(request):
    """Página principal: el usuario elige origen y destino, y ve la ruta en el mapa."""
    lat = request.GET.get("lat", "")
    lng = request.GET.get("lng", "")
    destino_id = request.GET.get("destino", "")

    resultado = None
    error = ""
    if "calcular" in request.GET:   # el usuario apretó el botón "Calcular ruta"
        resultado, error = calcular_resultado(lat, lng, destino_id)

    contexto = {
        "lugares": datos.LUGARES,
        "zonas": datos.ZONAS,
        "puntos_de_partida": datos.PUNTOS_DE_PARTIDA,
        "lat": lat,
        "lng": lng,
        "destino_id": destino_id,
        "resultado": resultado,
        "ruta": resultado["coordenadas"] if resultado else [],
        "error": error,
    }
    return render(request, "rutas/mapa.html", contexto)


def guardar_resena(request):
    """Guarda la reseña que envió el usuario. Devuelve un mensaje de error, o "" si salió bien."""
    if not request.user.is_authenticated:
        return "Primero inicia sesión para dejar una reseña."

    lugar_id = request.POST.get("lugar_id", "")
    calificacion = request.POST.get("calificacion", "")
    comentario = request.POST.get("comentario", "").strip()

    if buscar_lugar(lugar_id) is None:
        return "Ese lugar no existe."
    if calificacion not in ["1", "2", "3", "4", "5"]:
        return "Elige una calificación de 1 a 5."
    if comentario == "":
        return "Escribe un comentario."
    if len(comentario) > 500:
        return "El comentario puede tener hasta 500 caracteres."

    # Si el usuario ya había opinado sobre este lugar, se reemplaza su reseña; si no, se crea una nueva
    Resena.objects.update_or_create(
        lugar_id=lugar_id,
        usuario=request.user,
        defaults={"calificacion": int(calificacion), "comentario": comentario},
    )
    return ""


def lugares(request):
    """Lista de lugares con sus fotos y reseñas. También recibe el formulario para publicar una reseña."""
    error = ""
    if request.method == "POST":
        error = guardar_resena(request)
        if error == "":
            return redirect("lugares")   # volvemos a cargar la página para ver la reseña nueva

    items = []
    for lugar in datos.LUGARES:
        resenas = Resena.objects.filter(lugar_id=lugar["id"]).order_by("-fecha")
        total = 0
        for resena in resenas:
            total = total + resena.calificacion
        promedio = 0
        if len(resenas) > 0:
            promedio = round(total / len(resenas), 1)
        items.append({"lugar": lugar, "resenas": resenas, "cantidad": len(resenas), "promedio": promedio})

    return render(request, "rutas/lugares.html", {"items": items, "error": error})


def registro(request):
    """Crear una cuenta nueva."""
    formulario = UserCreationForm()
    if request.method == "POST":
        formulario = UserCreationForm(request.POST)
        if formulario.is_valid():
            usuario = formulario.save()   # guarda el usuario (la contraseña queda cifrada)
            login(request, usuario)       # y lo deja con la sesión iniciada
            return redirect("mapa")
    return render(request, "rutas/registro.html", {"formulario": formulario})


def iniciar_sesion(request):
    """Iniciar sesión con usuario y contraseña."""
    formulario = AuthenticationForm()
    if request.method == "POST":
        formulario = AuthenticationForm(request, data=request.POST)
        if formulario.is_valid():
            login(request, formulario.get_user())
            return redirect("mapa")
    return render(request, "rutas/login.html", {"formulario": formulario})


def salir(request):
    """Cerrar sesión. Solo se cierra si viene de un formulario (POST)."""
    if request.method == "POST":
        logout(request)
    return redirect("mapa")
