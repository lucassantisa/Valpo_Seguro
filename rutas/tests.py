# Pruebas automáticas. Se ejecutan con: python manage.py test
from unittest.mock import patch

import requests

from django.test import SimpleTestCase, override_settings

from . import calculos

# Una zona de ejemplo: un círculo de 100 m alrededor de este punto
ZONA = {"nombre": "Zona de prueba", "centro": [-33.040, -71.620], "radio": 100}
ZONAS = [ZONA]

# Ruta que pasa por el centro de la zona (de oeste a este) y otra que da la vuelta por el norte
RUTA_POR_LA_ZONA = {"coordenadas": [[-33.040, -71.623], [-33.040, -71.620], [-33.040, -71.617]], "distancia": 600, "duracion": 450}
RUTA_RODEO = {"coordenadas": [[-33.040, -71.623], [-33.043, -71.620], [-33.040, -71.617]], "distancia": 900, "duracion": 700}


class CalculosTests(SimpleTestCase):
    def test_distancia_entre_dos_puntos(self):
        # 0.001 grados de latitud son unos 111 metros
        distancia = calculos.distancia_metros([-33.000, -71.6], [-33.001, -71.6])
        self.assertAlmostEqual(distancia, 111, delta=2)

    def test_punto_dentro_y_fuera_de_la_zona(self):
        self.assertTrue(calculos.esta_en_zona([-33.040, -71.620], ZONA))
        self.assertFalse(calculos.esta_en_zona([-33.050, -71.620], ZONA))

    def test_metros_en_zonas(self):
        # La ruta atraviesa la zona por su centro: son unos 200 m (el diámetro del círculo)
        metros = calculos.metros_en_zonas(RUTA_POR_LA_ZONA["coordenadas"], ZONAS)
        self.assertAlmostEqual(metros["Zona de prueba"], 200, delta=15)

    def test_elige_la_ruta_que_no_pasa_por_la_zona(self):
        rutas = [dict(RUTA_POR_LA_ZONA), dict(RUTA_RODEO)]   # la más corta pasa por la zona
        elegida = calculos.elegir_ruta(rutas, ZONAS)
        self.assertEqual(elegida["distancia"], 900)
        self.assertEqual(elegida["zonas"], {})

    def test_sin_zonas_elige_la_primera_ruta(self):
        elegida = calculos.elegir_ruta([dict(RUTA_POR_LA_ZONA), dict(RUTA_RODEO)], [])
        self.assertEqual(elegida["distancia"], 600)


class FalsaRespuesta:
    """Imita la respuesta del servicio de rutas, para probar sin internet."""

    def __init__(self, datos, codigo=200):
        self.datos = datos
        self.status_code = codigo

    def json(self):
        return self.datos


class PedirRutasTests(SimpleTestCase):
    @patch("rutas.calculos.requests.get")
    def test_convierte_las_coordenadas_a_lat_lng(self, get):
        # El servicio entrega [longitud, latitud]; nosotros usamos [latitud, longitud]
        get.return_value = FalsaRespuesta({
            "code": "Ok",
            "routes": [{"distance": 812.4, "duration": 600.2, "geometry": {"coordinates": [[-71.6277, -33.0376], [-71.6298, -33.0434]]}}],
        })
        rutas, error = calculos.pedir_rutas([-33.0376, -71.6277], [-33.0434, -71.6298])
        self.assertEqual(error, "")
        self.assertEqual(rutas[0]["coordenadas"][0], [-33.0376, -71.6277])
        self.assertEqual(rutas[0]["distancia"], 812.4)

    @patch("rutas.calculos.requests.get")
    def test_si_no_hay_ruta_devuelve_un_error(self, get):
        get.return_value = FalsaRespuesta({"code": "NoRoute"})
        rutas, error = calculos.pedir_rutas([-33.0376, -71.6277], [-33.0434, -71.6298])
        self.assertEqual(rutas, [])
        self.assertIn("No se encontró", error)

    @patch("rutas.calculos.requests.get", side_effect=requests.RequestException)
    def test_si_no_hay_internet_devuelve_un_error(self, get):
        rutas, error = calculos.pedir_rutas([-33.0376, -71.6277], [-33.0434, -71.6298])
        self.assertEqual(rutas, [])
        self.assertIn("conexión a internet", error)


@override_settings(ORS_API_KEY="")
class VistasTests(SimpleTestCase):
    def test_la_pagina_principal_carga(self):
        respuesta = self.client.get("/")
        self.assertContains(respuesta, "Valpo Seguro")
        self.assertContains(respuesta, "Calcular ruta")

    def test_la_pagina_de_lugares_carga(self):
        respuesta = self.client.get("/lugares/")
        self.assertContains(respuesta, "Palacio Baburizza")

    def test_calcular_sin_punto_de_partida_muestra_un_error(self):
        respuesta = self.client.get("/", {"destino": "alegre", "calcular": "1"})
        self.assertContains(respuesta, "Primero elige tu punto de partida")

    def test_calcular_sin_destino_muestra_un_error(self):
        respuesta = self.client.get("/", {"lat": "-33.0376", "lng": "-71.6277", "calcular": "1"})
        self.assertContains(respuesta, "Primero elige un destino")

    @patch("rutas.calculos.pedir_rutas")
    def test_calcular_una_ruta_muestra_el_resultado(self, pedir_rutas):
        # Partimos desde fuera de las zonas y la ruta de prueba también va por fuera
        ruta = {"coordenadas": [[-33.0434, -71.6298], [-33.0423, -71.6265]], "distancia": 400, "duracion": 300}
        pedir_rutas.return_value = ([ruta], "")
        respuesta = self.client.get("/", {"lat": "-33.0434", "lng": "-71.6298", "destino": "concepcion", "calcular": "1"})
        self.assertContains(respuesta, "Ruta a Cerro Concepción")
        self.assertContains(respuesta, "400 m")
        self.assertContains(respuesta, "no pasa por las zonas")

    @patch("rutas.calculos.pedir_rutas")
    def test_si_la_ruta_pasa_por_una_zona_se_avisa(self, pedir_rutas):
        # Desde Plaza Sotomayor (dentro de Barrio Puerto) hacia Cerro Alegre
        ruta = {"coordenadas": [[-33.0376, -71.6277], [-33.0434, -71.6298]], "distancia": 700, "duracion": 600}
        pedir_rutas.return_value = ([ruta], "")
        respuesta = self.client.get("/", {"lat": "-33.0376", "lng": "-71.6277", "destino": "alegre", "calcular": "1"})
        self.assertContains(respuesta, "zonas de precaución")
        self.assertContains(respuesta, "Barrio Puerto")

    @patch("rutas.calculos.pedir_rutas")
    def test_si_el_servicio_falla_se_muestra_el_mensaje(self, pedir_rutas):
        pedir_rutas.return_value = ([], "No se pudo conectar con el servicio de rutas.")
        respuesta = self.client.get("/", {"lat": "-33.0376", "lng": "-71.6277", "destino": "alegre", "calcular": "1"})
        self.assertContains(respuesta, "No se pudo conectar")


# ---------- Pruebas de OpenRouteService (rutas que evitan zonas) ----------
ORIGEN = [-33.0434, -71.6298]    # Cerro Alegre: fuera de la zona de prueba
DESTINO = [-33.0423, -71.6265]   # Cerro Concepción: fuera de la zona de prueba


def respuesta_ors():
    """Imita lo que devuelve OpenRouteService cuando todo sale bien."""
    return FalsaRespuesta({"features": [{
        "geometry": {"coordinates": [[-71.6298, -33.0434], [-71.6265, -33.0423]]},
        "properties": {"summary": {"distance": 412.5, "duration": 300.2}},
    }]})


class OrsTests(SimpleTestCase):
    def test_el_circulo_se_convierte_en_un_poligono_cerrado(self):
        zona = {"nombre": "Z", "centro": [-33.04, -71.62], "radio": 100}
        puntos = calculos.circulo_a_poligono(zona)
        self.assertEqual(len(puntos), 17)            # 16 lados y el punto final que cierra
        self.assertEqual(puntos[0], puntos[-1])
        self.assertLess(puntos[0][0], -71)           # primero va la longitud...
        self.assertGreater(puntos[0][1], -34)        # ...y después la latitud
        for lng, lat in puntos:
            self.assertAlmostEqual(calculos.distancia_metros([lat, lng], zona["centro"]), 100, delta=3)

    def test_sin_clave_se_usa_osrm_y_no_se_evitan_zonas(self):
        with patch("rutas.calculos.pedir_rutas", return_value=([RUTA_RODEO], "")) as osrm, \
                patch("rutas.calculos.requests.post") as post:
            rutas, error, proveedor, evitando = calculos.buscar_rutas(ORIGEN, DESTINO, ZONAS, "")
        osrm.assert_called_once()
        post.assert_not_called()
        self.assertEqual((error, evitando), ("", False))
        self.assertIn("OSRM", proveedor)

    @patch("rutas.calculos.requests.post")
    def test_con_clave_se_le_pide_a_ors_que_evite_las_zonas(self, post):
        post.return_value = respuesta_ors()
        rutas, error, proveedor, evitando = calculos.buscar_rutas(ORIGEN, DESTINO, ZONAS, "mi-clave")
        cuerpo = post.call_args.kwargs["json"]
        evitar = cuerpo["options"]["avoid_polygons"]
        self.assertEqual(evitar["type"], "MultiPolygon")
        self.assertEqual(len(evitar["coordinates"]), 1)                 # una zona = un polígono
        self.assertEqual(cuerpo["coordinates"][0], [ORIGEN[1], ORIGEN[0]])   # ORS pide [longitud, latitud]
        self.assertEqual(post.call_args.kwargs["headers"], {"Authorization": "mi-clave"})
        self.assertEqual((error, proveedor, evitando), ("", "OpenRouteService", True))
        self.assertEqual(rutas[0]["coordenadas"][0], ORIGEN)            # y nosotros volvemos a [lat, lng]

    @patch("rutas.calculos.requests.post")
    def test_no_se_evita_la_zona_donde_esta_el_origen(self, post):
        post.return_value = respuesta_ors()
        dentro_de_la_zona = [-33.040, -71.620]
        rutas, error, proveedor, evitando = calculos.buscar_rutas(dentro_de_la_zona, DESTINO, ZONAS, "mi-clave")
        self.assertNotIn("options", post.call_args.kwargs["json"])      # no hay nada que evitar
        self.assertFalse(evitando)

    @patch("rutas.calculos.requests.post")
    def test_si_las_zonas_bloquean_la_ruta_se_reintenta_sin_evitar(self, post):
        post.side_effect = [FalsaRespuesta({}, 404), respuesta_ors()]
        rutas, error, proveedor, evitando = calculos.buscar_rutas(ORIGEN, DESTINO, ZONAS, "mi-clave")
        self.assertEqual(post.call_count, 2)
        self.assertNotIn("options", post.call_args_list[1].kwargs["json"])
        self.assertEqual(error, "")
        self.assertFalse(evitando)

    @patch("rutas.calculos.requests.post")
    def test_una_clave_invalida_muestra_un_error_y_no_se_reintenta(self, post):
        post.return_value = FalsaRespuesta({}, 401)
        rutas, error, proveedor, evitando = calculos.buscar_rutas(ORIGEN, DESTINO, ZONAS, "clave-mala")
        self.assertEqual(post.call_count, 1)
        self.assertEqual(rutas, [])
        self.assertIn("clave", error)

    @patch("rutas.calculos.requests.post", side_effect=requests.RequestException)
    def test_si_no_hay_internet_muestra_un_error(self, post):
        rutas, error, proveedor, evitando = calculos.buscar_rutas(ORIGEN, DESTINO, ZONAS, "mi-clave")
        self.assertEqual(rutas, [])
        self.assertIn("conexión a internet", error)

    @override_settings(ORS_API_KEY="clave-de-prueba")
    @patch("rutas.calculos.buscar_rutas")
    def test_la_vista_usa_la_clave_y_muestra_que_se_evitaron_las_zonas(self, buscar_rutas):
        ruta = {"coordenadas": [[-33.0434, -71.6298], [-33.0423, -71.6265]], "distancia": 400, "duracion": 300}
        buscar_rutas.return_value = ([ruta], "", "OpenRouteService", True)
        respuesta = self.client.get("/", {"lat": "-33.0434", "lng": "-71.6298", "destino": "concepcion", "calcular": "1"})
        self.assertEqual(buscar_rutas.call_args.args[3], "clave-de-prueba")
        self.assertContains(respuesta, "OpenRouteService")
        self.assertContains(respuesta, "evite las zonas de precaución")
