# Valpo Seguro

Proyecto desarrollado en Python y Django. Es una aplicación web pensada para turistas en Valparaíso que permite calcular rutas a pie hacia distintos puntos de interés, evitando las zonas de precaución marcadas en el mapa.

## Integrantes
- Diego Casas
- Lucas Santis
- Alejandro Fuenzalida
- Martina Torrejón

---

## ¿Qué hace el proyecto?

La función principal es trazar recorridos caminando por Valparaíso y verificar si la ruta pasa por alguno de los sectores de riesgo que definimos previamente.

El flujo funciona en tres pasos:
1. **Entrada:** El usuario selecciona su punto de partida usando su ubicación actual, marcando un punto directo en el mapa o eligiendo uno de los puntos de ejemplo, y escoge un destino turístico.
2. **Procesamiento:** El backend en Django consulta un servicio de mapas para obtener el trayecto peatonal y calcula si cruza alguna zona de precaución. Con una clave de OpenRouteService configurada, el sistema solicita un desvío real para rodear esas áreas; sin la clave, utiliza OSRM y advierte al usuario si el camino pasa por algún sector de cuidado.
3. **Resultado:** Se muestra la ruta dibujada en el mapa junto con la distancia en metros, el tiempo estimado a pie y una alerta indicando si el trayecto es seguro o si cruza zonas de precaución.

### Funcionalidades adicionales:
- **Cuentas de usuario:** Permite registrarse e iniciar sesión con usuario y contraseña desde `/registro/` y `/ingresar/`.
- **Reseñas:** En la sección **Lugares** ubicada en `/lugares/`, los usuarios registrados pueden dejar una calificación del 1 al 5 y un comentario en cada atractivo turístico.

---

## Cómo ejecutar el proyecto

Para correr la aplicación se necesita **Python 3.12 o superior** y **conexión a internet** para cargar el mapa y calcular las rutas.

Abre PowerShell o CMD en la carpeta raíz del proyecto y ejecuta los siguientes comandos:

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

El comando `migrate` crea la base de datos local para guardar usuarios y reseñas; solo es necesario correrlo la primera vez.

Una vez iniciado el servidor, abre en el navegador: **http://127.0.0.1:8000/**

---

## Configuración de OpenRouteService

Para que el mapa calcule desvíos reales y esquive las zonas peligrosas en lugar de solo advertir sobre ellas, es necesario configurar un token gratuito:

1. Crea una cuenta en [openrouteservice.org](https://openrouteservice.org) y genera una API key.
2. En la carpeta principal del proyecto, haz una copia del archivo `.env.example` y cámbiale el nombre a `.env`.
3. Abre el archivo `.env` y pega tu clave después de `ORS_API_KEY=` sin espacios ni comillas.
4. Detén el servidor presionando `Ctrl + C` y vuelve a iniciarlo con `python manage.py runserver`.

---

## Casos de prueba

En `rutas/datos.py` dejamos precargados 6 lugares turísticos, 3 zonas de precaución y 3 puntos de partida de ejemplo para probar la aplicación rápidamente:

- **Caso 1 — Ruta segura:** Selecciona *"Cerro Alegre"* como punto de partida y *"Cerro Concepción"* como destino. Debería trazar la ruta y mostrar un aviso verde indicando que no pasa por zonas de precaución.
- **Caso 2 — Ruta con advertencia:** Selecciona *"Plaza Sotomayor"* como punto de partida y *"Cerro Alegre"* como destino. Calculará el recorrido, pero mostrará una alerta amarilla porque el punto de inicio está dentro de la zona "Barrio Puerto".
- **Caso 3 — Validación de datos:** Si presionas *"Calcular ruta"* sin haber elegido un inicio, el sistema mostrará un mensaje solicitando seleccionar primero el punto de partida.

---

## Estructura del proyecto

- `config/`: Configuración general del proyecto Django y archivo principal de URLs.
- `rutas/`: Aplicación principal donde se encuentra la lógica del sistema:
  - `datos.py`: Coordenadas de los atractivos turísticos, zonas de precaución y puntos de ejemplo.
  - `calculos.py`: Funciones encargadas de consultar las rutas y detectar intersecciones con las zonas de riesgo.
  - `models.py`: Modelo de base de datos para almacenar las reseñas de los usuarios.
  - `views.py`: Controladores que reciben las peticiones del usuario y envían los datos a las vistas.
  - `templates/rutas/`: Archivos HTML de la interfaz.
  - `static/rutas/fotos/`: Imágenes de los puntos turísticos.
