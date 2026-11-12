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
    "django.contrib.staticfiles",    # para las fotos
    "django.contrib.contenttypes",   # necesario para los usuarios
    "django.contrib.auth",           # usuarios, contraseñas e inicio de sesión
    "django.contrib.sessions",       # recuerda quién inició sesión
    "rutas",
]

MIDDLEWARE = [
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",                   # protege los formularios
    "django.contrib.auth.middleware.AuthenticationMiddleware",     # sabe qué usuario está conectado
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,   # busca los .html dentro de rutas/templates/
        "OPTIONS": {"context_processors": [
            "django.template.context_processors.request",
            "django.contrib.auth.context_processors.auth",   # permite usar "user" en los .html
        ]},
    },
]

WSGI_APPLICATION = "config.wsgi.application"

# Base de datos SQLite (un archivo, db.sqlite3). Guarda los usuarios y las reseñas.
# Los lugares y las zonas siguen estando en rutas/datos.py.
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# Reglas para las contraseñas (rechaza las muy cortas, las muy comunes y las que son solo números)
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

LANGUAGE_CODE = "es-cl"
TIME_ZONE = "America/Santiago"

STATIC_URL = "static/"

# Clave de OpenRouteService. Si está vacía, la aplicación igual funciona (con el servicio OSRM, sin evitar zonas).
ORS_API_KEY = os.environ.get("ORS_API_KEY", "").strip()
