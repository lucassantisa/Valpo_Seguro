from django.conf import settings
from django.shortcuts import render

from . import calculos, datos


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


def lugares(request):
    """Lista de lugares con su descripción, horario y fotos."""
    return render(request, "rutas/lugares.html", {"lugares": datos.LUGARES})
