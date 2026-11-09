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


# ----------------------------------------------------------------------------------------------
# Rutas que EVITAN las zonas de precaución, usando OpenRouteService (necesita una clave gratuita)
# ----------------------------------------------------------------------------------------------
SIN_RUTA = "No se encontró una ruta a pie entre esos puntos."


def circulo_a_poligono(zona, lados=16):
    """Convierte el círculo de una zona en un polígono de 16 puntos [longitud, latitud].
    OpenRouteService no entiende círculos: necesita polígonos para saber qué áreas evitar."""
    lat, lng = zona["centro"]
    puntos = []
    for i in range(lados):
        angulo = 2 * math.pi * i / lados
        # 110540 m es un grado de latitud; un grado de longitud mide menos cuanto más lejos del ecuador
        dif_lat = zona["radio"] * math.sin(angulo) / 110540
        dif_lng = zona["radio"] * math.cos(angulo) / (111320 * math.cos(math.radians(lat)))
        puntos.append([lng + dif_lng, lat + dif_lat])   # OpenRouteService pide primero la longitud
    puntos.append(puntos[0])   # el polígono se cierra volviendo al primer punto
    return puntos


def pedir_rutas_ors(origen, destino, zonas_a_evitar, clave):
    """Le pide a OpenRouteService una ruta a pie que NO pase por las zonas indicadas.
    Devuelve (lista_de_rutas, mensaje_de_error), igual que pedir_rutas."""
    url = "https://api.openrouteservice.org/v2/directions/foot-walking/geojson"
    cuerpo = {"coordinates": [[origen[1], origen[0]], [destino[1], destino[0]]]}

    if len(zonas_a_evitar) > 0:
        poligonos = []
        for zona in zonas_a_evitar:
            poligonos.append([circulo_a_poligono(zona)])
        cuerpo["options"] = {"avoid_polygons": {"type": "MultiPolygon", "coordinates": poligonos}}

    try:
        respuesta = requests.post(url, json=cuerpo, headers={"Authorization": clave}, timeout=15)
    except requests.RequestException:
        return [], "No se pudo conectar con el servicio de rutas. Revisa tu conexión a internet."

    if respuesta.status_code in (401, 403):
        return [], "La clave de OpenRouteService no es válida. Revisa tu archivo .env."
    if respuesta.status_code == 429:
        return [], "Se alcanzó el límite diario de consultas de OpenRouteService. Inténtalo más tarde."
    if respuesta.status_code != 200:
        return [], SIN_RUTA

    try:
        ruta = respuesta.json()["features"][0]
        coordenadas = []
        for lng, lat in ruta["geometry"]["coordinates"]:
            coordenadas.append([lat, lng])
        resumen = ruta["properties"]["summary"]
        return [{"coordenadas": coordenadas, "distancia": resumen["distance"], "duracion": resumen["duration"]}], ""
    except (KeyError, IndexError, ValueError):
        return [], "El servicio de rutas respondió algo inesperado. Inténtalo de nuevo."


def buscar_rutas(origen, destino, zonas, clave):
    """Decide cómo pedir las rutas. Devuelve (rutas, error, proveedor, evitando).
    - Sin clave: usa OSRM, que solo entrega una ruta alternativa (no puede evitar zonas).
    - Con clave: usa OpenRouteService y le pide que evite las zonas."""
    if clave == "":
        rutas, error = pedir_rutas(origen, destino)
        return rutas, error, "OSRM (sin clave)", False

    # Las zonas donde ya estamos parados (el origen o el destino están adentro) no se pueden evitar
    zonas_a_evitar = []
    for zona in zonas:
        if not esta_en_zona(origen, zona) and not esta_en_zona(destino, zona):
            zonas_a_evitar.append(zona)

    if len(zonas_a_evitar) > 0:
        rutas, error = pedir_rutas_ors(origen, destino, zonas_a_evitar, clave)
        if error == "":
            return rutas, "", "OpenRouteService", True
        if error != SIN_RUTA:
            return [], error, "OpenRouteService", False
        # Si las zonas bloquean todos los caminos, calculamos la ruta sin evitarlas y la página avisará

    rutas, error = pedir_rutas_ors(origen, destino, [], clave)
    return rutas, error, "OpenRouteService", False
