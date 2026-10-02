import os
import shutil
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "dev-only-change-me-before-deploying")

DEBUG = os.environ.get("DJANGO_DEBUG", "1") == "1"
#DEBUG = True

ALLOWED_HOSTS = os.environ.get(
    "DJANGO_ALLOWED_HOSTS", 
    "localhost,127.0.0.1,testserver,qiksearch.jefftarimo.co.ke"
).split(",")

# Application definition
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.humanize",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sitemaps",
    "catalog",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "qikstore.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "catalog.context_processors.site_settings",
            ],
        },
    },
]

WSGI_APPLICATION = "qikstore.wsgi.application"

# Database: copy existing SQLite file to writable /tmp on serverless environments
IS_SERVERLESS = os.environ.get("AWS_EXECUTION_ENV") is not None or "/var/task" in str(BASE_DIR)

if IS_SERVERLESS:
    DB_PATH = Path("/tmp") / "db.sqlite3"
    SOURCE_DB = BASE_DIR / "db.sqlite3"
    if not DB_PATH.exists() and SOURCE_DB.exists():
        try:
            shutil.copyfile(SOURCE_DB, DB_PATH)
        except OSError:
            pass
else:
    DB_PATH = BASE_DIR / "db.sqlite3"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": DB_PATH,
    }
}

# Internationalization
LANGUAGE_CODE = "en-ke"
TIME_ZONE = "Africa/Nairobi"
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"]

# Media files (User uploaded)
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage"
    },
    "staticfiles": {
        "BACKEND": (
            "django.contrib.staticfiles.storage.StaticFilesStorage"
            if DEBUG
            else "whitenoise.storage.CompressedManifestStaticFilesStorage"
        )
    },
}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Store session data inside signed, client-side HTTP cookies instead of SQLite
SESSION_ENGINE = "django.contrib.sessions.backends.signed_cookies"

# Security & Cookies
# SECURE_CONTENT_TYPE_NOSNIFF = True
# X_FRAME_OPTIONS = "DENY"
# CSRF_COOKIE_SECURE = not DEBUG
# SESSION_COOKIE_SECURE = not DEBUG
# SESSION_COOKIE_HTTPONLY = True

# Production SSL / HSTS settings
# SECURE_SSL_REDIRECT = os.environ.get("DJANGO_SECURE_SSL_REDIRECT", "0") == "1"
# SECURE_HSTS_SECONDS = int(os.environ.get("DJANGO_SECURE_HSTS_SECONDS", "0"))
# SECURE_HSTS_INCLUDE_SUBDOMAINS = os.environ.get("DJANGO_SECURE_HSTS_INCLUDE_SUBDOMAINS", "0") == "1"
# SECURE_HSTS_PRELOAD = os.environ.get("DJANGO_SECURE_HSTS_PRELOAD", "0") == "1"

# if os.environ.get("DJANGO_TRUST_X_FORWARDED_PROTO", "0") == "1":
#     SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")