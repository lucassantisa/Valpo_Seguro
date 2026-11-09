# Valpo Seguro (Entregable III: funcionalidad corazón)

Aplicación web hecha con Django para turistas en Valparaíso. La **funcionalidad corazón** es calcular una
**ruta a pie** hasta un lugar patrimonial **evitando las zonas de precaución**.

1. **Entrada:** el usuario elige su punto de partida (su ubicación, un punto en el mapa o un punto de ejemplo) y un lugar de destino.
2. **Procesamiento:** Django le pide una ruta a pie a un servicio de internet y mide cuántos metros pasan por zonas de precaución.
   Con una clave de OpenRouteService (opcional) le pide que **evite** las zonas; sin clave usa OSRM, elige la alternativa que pasa menos
   por ellas y avisa.
3. **Salida:** la página muestra la ruta en el mapa, la distancia, el tiempo a pie y un aviso con las zonas por las que pasa.

## Cómo ejecutarlo en tu computador (localhost)

Necesitas Python 3.12 o más nuevo e **internet** (el mapa y el cálculo de rutas usan servicios en línea).
La aplicación funciona **sin clave** (modo OSRM). Para que las rutas **evite**n las zonas hace falta la clave de OpenRouteService (ver más abajo).

```
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python manage.py runserver
```

(En Mac o Linux, el segundo comando es `source venv/bin/activate`.)

Luego abre http://127.0.0.1:8000/ en el navegador. No hace falta crear una base de datos ni ejecutar `migrate`.

## Clave de OpenRouteService (opcional, para evitar zonas de verdad)

1. Crea una cuenta gratuita en https://openrouteservice.org y genera una clave (*token*).
2. En la carpeta del proyecto (donde está `manage.py`), copia `.env.example` con el nombre `.env`:
   ```
   copy .env.example .env
   ```
3. Abre `.env` y pega la clave después de `ORS_API_KEY=` (sin comillas ni espacios).
4. Reinicia el servidor (`Ctrl + C` y `python manage.py runserver`).

Si funciona, el resultado de cada ruta dice "Ruta calculada con OpenRouteService, pidiéndole que evite las zonas de precaución".
El archivo `.env` **no se sube a GitHub** (está en `.gitignore`): la clave es personal y no se debe compartir.

## Datos para probar la funcionalidad corazón

Los datos están precargados en `rutas/datos.py`: 6 lugares, 3 zonas de precaución y 3 puntos de partida de ejemplo.

| Caso | Punto de partida | Destino | Qué debería pasar |
|---|---|---|---|
| 1. Principal | Punto de ejemplo "Cerro Alegre" | Cerro Concepción | Se dibuja la ruta, con distancia y tiempo, y aparece el mensaje verde de que no pasa por zonas |
| 2. Alternativo | Punto de ejemplo "Plaza Sotomayor" | Cerro Alegre | Se dibuja la ruta y aparece un aviso amarillo, porque el punto de partida está dentro de la zona "Barrio Puerto" |
| 3. Error | Ninguno | Cualquiera | Aparece el mensaje "Primero elige tu punto de partida" |

Pasos: elige el punto de partida, elige el destino y presiona **Calcular ruta**.

## Pruebas automáticas

```
python manage.py test
```

## Estructura del proyecto

```
valpo_seguro/
├── manage.py               controla el proyecto (runserver, test)
├── requirements.txt        librerías que hay que instalar
├── .env.example            plantilla del archivo .env (clave de OpenRouteService)
├── config/
│   ├── settings.py         configuración
│   ├── urls.py             manda todas las direcciones a la app "rutas"
│   └── wsgi.py             conexión con el servidor
└── rutas/                  nuestra app
    ├── datos.py            lugares, zonas y puntos de partida
    ├── calculos.py         procesamiento: pedir rutas (OSRM u OpenRouteService), medir zonas y elegir la mejor
    ├── views.py            recibe lo que elige el usuario y prepara el resultado
    ├── urls.py             direcciones de la app (/ y /lugares/)
    ├── tests.py            pruebas automáticas
    ├── templates/rutas/    páginas HTML (base, mapa y lugares)
    └── static/rutas/fotos/ fotos de los lugares
```

## Limitaciones de esta versión

- Si el servicio de rutas no responde (por ejemplo, sin internet o con una clave inválida), la página muestra un mensaje de error.
- Sin clave, el servicio OSRM ofrece una ruta alternativa como máximo; si ninguna evita las zonas, la app avisa por cuáles pasa.
- Con clave, las zonas que contienen el punto de partida o el destino no se pueden evitar: solo se avisa. Si las zonas bloquean todos los caminos, se calcula la ruta sin evitarlas y se avisa.
- La clave gratuita de OpenRouteService tiene un límite diario de consultas.
- Las zonas de precaución son círculos marcados por el equipo y no garantizan seguridad.
- Esta versión no usa base de datos, cuentas de usuario ni panel de administración: los datos están en `rutas/datos.py`.
