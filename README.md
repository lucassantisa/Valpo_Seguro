# Valpo Seguro

Aplicación web hecha con Django para turistas en Valparaíso. La **funcionalidad corazón** es calcular una
**ruta a pie** hasta un lugar patrimonial **evitando las zonas de precaución**.

1. **Entrada:** el usuario elige su punto de partida (su ubicación, un punto en el mapa o un punto de ejemplo) y un lugar de destino.
2. **Procesamiento:** Django le pide rutas a pie a un servicio de internet (OSRM), mide cuántos metros de cada ruta pasan por zonas
   de precaución y elige la que pasa menos.
3. **Salida:** la página muestra la ruta en el mapa, la distancia, el tiempo a pie y un aviso con las zonas por las que pasa.

## Cómo ejecutarlo en tu computador (localhost)

Necesitas Python 3.12 o más nuevo e **internet** (el mapa y el cálculo de rutas usan servicios en línea).

```
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python manage.py runserver
```

(En Mac o Linux, el segundo comando es `source venv/bin/activate`.)

Luego abre http://127.0.0.1:8000/ en el navegador. No hace falta crear una base de datos ni ejecutar `migrate`.
