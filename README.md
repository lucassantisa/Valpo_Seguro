# Valpo Seguro

Proyecto del ramo hecho con Python y Django. Es una página web para que los turistas en Valparaíso puedan buscar cómo llegar caminando a lugares conocidos tratando de no pasar por sectores peligrosos.

## Integrantes
- Diego Casas
- Lucas Santis
- Alejandro Fuenzalida
- Martina Torrejón

---

## ¿De qué trata el proyecto?

La función principal de la página es calcular rutas a pie hacia distintos puntos turísticos de Valparaíso y revisar si el camino pasa por alguna de las zonas de precaución que dejamos marcadas en el mapa.

El funcionamiento básico es así:
1. **El usuario elige:** Pone desde dónde sale (puede usar su ubicación actual, pinchar directo en el mapa o usar uno de los puntos de ejemplo que dejamos listos) y elige el destino turístico al que quiere ir.
2. **El programa calcula:** Por detrás, Django le pide a una API de mapas el recorrido a pie y calcula si la línea de la ruta cruza alguna zona peligrosa. Si se le pone una clave de OpenRouteService, el mapa busca un desvío real para rodear la zona; si no se le pone clave, usa OSRM y te avisa por cuáles sectores peligrosos vas a pasar.
3. **Muestra el resultado:** Dibuja la ruta en el mapa, dice cuántos metros son, cuánto tiempo demora aproximadamente caminando y muestra un mensaje (verde si vas seguro o amarillo si hay que tener cuidado).

### Otras cosas que agregamos:
- **Registro e inicio de sesión:** Se pueden crear cuentas y entrar con usuario y contraseña (`/registro/` y `/ingresar/`).
- **Reseñas:** En la pestaña de **Lugares** (`/lugares/`), si tienes sesión iniciada puedes dejar un comentario y ponerle nota (del 1 al 5) a cada lugar turístico.

---

## Cómo correr la página en tu compu

Para probarlo necesitas tener **Python (3.12 o más nuevo)** instalado y estar conectado a **internet** (porque el mapa y el cálculo de calles se cargan desde internet).

1. Abre la terminal en la carpeta del proyecto y crea el entorno virtual:
```bash
python -m venv venv
```

2. Activa el entorno:
- En Windows:
```bash
venv\Scripts\activate
```
- En Mac o Linux:
```bash
source venv/bin/activate
```

3. Instala lo que está en el `requirements.txt`:
```bash
pip install -r requirements.txt
```

4. Crea la base de datos (solo se hace la primera vez para que guarden los usuarios y las reseñas):
```bash
python manage.py migrate
```

5. Prende el servidor:
```bash
python manage.py runserver
```

6. Entra desde tu navegador a: **http://127.0.0.1:8000/**

---

## Clave de OpenRouteService

El programa no esquiva las zonas peligrosas sin el token.

1. Créate una cuenta gratis en [openrouteservice.org](https://openrouteservice.org) y genera un token.
2. Duplica el archivo `.env.example` que está en la carpeta principal y cámbiale el nombre a `.env`.
3. Abre el `.env` y pega tu clave al lado de `ORS_API_KEY=` (sin espacios ni comillas).
4. Apaga el servidor (`Ctrl + C`) y vuélvelo a prender con `python manage.py runserver`.

---

## Ejemplos para probar que funciona

Dejamos unos datos listos en `rutas/datos.py` (6 lugares turísticos, 3 zonas peligrosas y 3 puntos de inicio de ejemplo) para no tener que andar buscando coordenadas a mano:

- **Caso 1 (Ruta limpia):** Elige el punto de ejemplo *"Cerro Alegre"* como inicio y *"Cerro Concepción"* como destino. Debería dibujar la ruta y salir un cuadro verde diciendo que no pasa por zonas de precaución.
- **Caso 2 (Ruta con aviso):** Elige *"Plaza Sotomayor"* como inicio y *"Cerro Alegre"* como destino. Va a calcular la ruta pero te saldrá una alerta amarilla porque la plaza está justo dentro de la zona de cuidado "Barrio Puerto".
- **Caso 3 (Si falta un dato):** Si aprietas *"Calcular ruta"* sin haber elegido dónde partes, te sale un aviso pidiendo que elijas primero el punto de partida.

---

## Cómo ordenamos los archivos

- `config/`: Archivos de configuración del proyecto Django y las URLs generales.
- `rutas/`: La app principal donde está todo nuestro código:
  - `datos.py`: Listas con las coordenadas de los lugares, las zonas de cuidado y los puntos de ejemplo.
  - `calculos.py`: Las funciones que piden las rutas a internet y revisan si chocan con los círculos de precaución.
  - `models.py`: La tabla de la base de datos para guardar las reseñas.
  - `views.py`: Lo que recibe los clics del usuario y manda los datos a los HTML.
  - `templates/rutas/`: Las páginas HTML.
  - `static/rutas/fotos/`: Las fotos de los lugares turísticos.



