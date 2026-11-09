# Configuración del proyecto. Solo dejamos lo que usamos.
import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

# Lee el archivo .env, donde guardamos la clave de OpenRouteService (ese archivo NO se sube a GitHub)
load_dotenv(BASE_DIR / ".env")

SECRET_KEY = "clave-solo-para-desarrollo"
DEBUG = True
ALLOWED_HOSTS = []

# Apps que usa el proyecto: "rutas" es la nuestra.
INSTALLED_APPS = [
    "django.contrib.staticfiles",   # para las fotos
    "rutas",
]

MIDDLEWARE = [
    "django.middleware.common.CommonMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,   # busca los .html dentro de rutas/templates/
        "OPTIONS": {"context_processors": ["django.template.context_processors.request"]},
    },
]

WSGI_APPLICATION = "config.wsgi.application"

# Para esta entrega no usamos base de datos: los lugares y zonas están en rutas/datos.py
DATABASES = {}

LANGUAGE_CODE = "es-cl"
TIME_ZONE = "America/Santiago"

STATIC_URL = "static/"

# Clave de OpenRouteService. Si está vacía, la aplicación igual funciona (con el servicio OSRM, sin evitar zonas).
ORS_API_KEY = os.environ.get("ORS_API_KEY", "").strip()
