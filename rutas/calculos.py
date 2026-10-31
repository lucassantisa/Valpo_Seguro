# Aquí está el procesamiento de la funcionalidad corazón:
# pedir rutas a pie, medir cuánto pasan por zonas de precaución y elegir la mejor.
import math

import requests


def distancia_metros(punto1, punto2):
    """Distancia en metros entre dos puntos [lat, lng] (fórmula de haversine)."""
    radio_tierra = 6371000
    lat1 = math.radians(punto1[0])
    lat2 = math.radians(punto2[0])
    dif_lat = lat2 - lat1
    dif_lng = math.radians(punto2[1] - punto1[1])
    a = math.sin(dif_lat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dif_lng / 2) ** 2
    return 2 * radio_tierra * math.asin(math.sqrt(a))


def esta_en_zona(punto, zona):
    """True si el punto está dentro del círculo de la zona."""
    return distancia_metros(punto, zona["centro"]) <= zona["radio"]


def metros_en_zonas(coordenadas, zonas):
    """Cuántos metros de la ruta pasan por cada zona. Devuelve algo como {"Barrio Puerto": 120.0}."""
    metros = {}
    for i in range(len(coordenadas) - 1):
        a = coordenadas[i]
        b = coordenadas[i + 1]
        largo = distancia_metros(a, b)
        pasos = int(largo / 10) + 1   # revisamos un punto cada 10 metros más o menos
        for k in range(pasos):
            punto = [a[0] + (b[0] - a[0]) * k / pasos, a[1] + (b[1] - a[1]) * k / pasos]
            for zona in zonas:
                if esta_en_zona(punto, zona):
                    metros[zona["nombre"]] = metros.get(zona["nombre"], 0) + largo / pasos
    return metros


def elegir_ruta(rutas, zonas):
    """De todas las rutas posibles, elige la que pasa menos metros por zonas de precaución."""
    mejor_ruta = None
    menos_metros = None
    for ruta in rutas:
        por_zona = metros_en_zonas(ruta["coordenadas"], zonas)
        total = sum(por_zona.values())
        if mejor_ruta is None or total < menos_metros:
            mejor_ruta = ruta
            menos_metros = total
            mejor_ruta["zonas"] = por_zona
    return mejor_ruta


def pedir_rutas(origen, destino):
    """Le pide rutas a pie a un servicio de internet (OSRM). Devuelve (lista_de_rutas, mensaje_de_error)."""
    url = "https://routing.openstreetmap.de/routed-foot/route/v1/driving/%s,%s;%s,%s" % (
        origen[1], origen[0], destino[1], destino[0])
    parametros = {"overview": "full", "geometries": "geojson", "alternatives": "true"}

    try:
        respuesta = requests.get(url, params=parametros, timeout=15)
        datos = respuesta.json()
    except (requests.RequestException, ValueError):
        return [], "No se pudo conectar con el servicio de rutas. Revisa tu conexión a internet."

    if datos.get("code") != "Ok":
        return [], "No se encontró una ruta a pie entre esos puntos."

    rutas = []
    for r in datos["routes"]:
        coordenadas = []
        for lng, lat in r["geometry"]["coordinates"]:   # el servicio entrega primero la longitud
            coordenadas.append([lat, lng])
        rutas.append({"coordenadas": coordenadas, "distancia": r["distance"], "duracion": r["duration"]})
    return rutas, ""
