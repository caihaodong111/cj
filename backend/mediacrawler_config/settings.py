# -*- coding: utf-8 -*-
# Django settings for MediaCrawler Backend
# Reference .env: /Users/caihd/Desktop/MediaCrawler-main/backend/.env

import os
from pathlib import Path
from django.core.exceptions import ImproperlyConfigured

BASE_DIR = Path(__file__).resolve().parent.parent

# Load .env from backend directory
from dotenv import load_dotenv
env_path = BASE_DIR / '.env'
if env_path.exists():
    load_dotenv(env_path)

# Django Secret Key
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'django-insecure-dev-key-change-in-production')

# Debug Mode
DEBUG = os.environ.get('DJANGO_DEBUG', 'True') == 'True'

ALLOWED_HOSTS = [
    host.strip()
    for host in os.environ.get('DJANGO_ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')
    if host.strip()
]

# Installed Apps
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "api.apps.ApiConfig",
    "media_platform.apps.MediaPlatformConfig",
    "rest_framework",
    "corsheaders",
    "django_filters",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "mediacrawler_config.urls"

TEMPLATES = [{
    "BACKEND": "django.template.backends.django.DjangoTemplates",
    "DIRS": [BASE_DIR / "templates"],
    "APP_DIRS": True,
    "OPTIONS": {
        "context_processors": [
            "django.template.context_processors.debug",
            "django.template.context_processors.request",
            "django.contrib.auth.context_processors.auth",
            "django.contrib.messages.context_processors.messages",
        ],
    },
}]

WSGI_APPLICATION = "mediacrawler_config.wsgi.application"

# Database
SUPPORTED_DB_ENGINES = {
    "mysql": "mysql",
    "postgres": "postgresql",
    "postgresql": "postgresql",
}


def _get_env(name: str, default: str = "") -> str:
    value = os.environ.get(name)
    if value is None:
        return default
    return value.strip()


def _normalize_db_engine(raw_engine: str) -> str:
    normalized = (raw_engine or "mysql").strip().lower()
    try:
        return SUPPORTED_DB_ENGINES[normalized]
    except KeyError as exc:
        supported = ", ".join(sorted(SUPPORTED_DB_ENGINES))
        raise ImproperlyConfigured(
            f"Unsupported DB_ENGINE '{raw_engine}'. Supported values: {supported}."
        ) from exc


def _require_database_setting(name: str, value: str, engine: str) -> str:
    if value:
        return value
    raise ImproperlyConfigured(f"{name} must be set when DB_ENGINE='{engine}'.")


DB_ENGINE = _normalize_db_engine(os.environ.get("DB_ENGINE"))
DB_NAME = ""
DB_USER = ""
DB_PASSWORD = ""
DB_HOST = ""
DB_PORT = ""

if DB_ENGINE == "mysql":
    import pymysql

    pymysql.__version__ = "2.2.1"
    pymysql.version_info = (2, 2, 1, "final", 0)
    pymysql.install_as_MySQLdb()

    DB_NAME = _get_env("DB_NAME") or _get_env("MYSQL_DB_NAME", "media_crawler")
    DB_USER = _get_env("DB_USER") or _get_env("MYSQL_DB_USER", "root")
    DB_PASSWORD = (
        _get_env("DB_PASSWORD")
        or _get_env("MYSQL_DB_PASSWORD")
        or _get_env("MYSQL_DB_PWD")
    )
    DB_HOST = _get_env("DB_HOST") or _get_env("MYSQL_DB_HOST", "localhost")
    DB_PORT = _get_env("DB_PORT") or _get_env("MYSQL_DB_PORT", "3306")

    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.mysql",
            "NAME": DB_NAME,
            "USER": DB_USER,
            "PASSWORD": DB_PASSWORD,
            "HOST": DB_HOST,
            "PORT": DB_PORT,
            "OPTIONS": {
                "charset": "utf8mb4",
                "init_command": "SET sql_mode='STRICT_TRANS_TABLES'",
            },
        }
    }
else:
    DB_NAME = _require_database_setting(
        "DB_NAME",
        _get_env("DB_NAME") or _get_env("POSTGRES_DB_NAME"),
        DB_ENGINE,
    )
    DB_USER = _get_env("DB_USER") or _get_env("POSTGRES_DB_USER", "postgres")
    DB_PASSWORD = (
        _get_env("DB_PASSWORD")
        or _get_env("POSTGRES_DB_PASSWORD")
        or _get_env("POSTGRES_DB_PWD")
    )
    DB_HOST = _get_env("DB_HOST") or _get_env("POSTGRES_DB_HOST", "localhost")
    DB_PORT = _get_env("DB_PORT") or _get_env("POSTGRES_DB_PORT", "5432")

    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": DB_NAME,
            "USER": DB_USER,
            "PASSWORD": DB_PASSWORD,
            "HOST": DB_HOST,
            "PORT": DB_PORT,
        }
    }

# Password Validation
AUTH_PASSWORD_VALIDATORS = [
    "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    "django.contrib.auth.password_validation.MinimumLengthValidator",
    "django.contrib.auth.password_validation.CommonPasswordValidator",
    "django.contrib.auth.password_validation.NumericPasswordValidator",
]

# Internationalization
LANGUAGE_CODE = "zh-hans"
TIME_ZONE = "Asia/Shanghai"
USE_I18N = True
USE_TZ = True

# Static & Media
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# REST Framework
REST_FRAMEWORK = {
    "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.AllowAny"],
    "DEFAULT_RENDERER_CLASSES": ["rest_framework.renderers.JSONRenderer"],
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 100,
    "DEFAULT_FILTER_BACKENDS": [
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.OrderingFilter",
        "rest_framework.filters.SearchFilter",
    ],
}

# CORS
CORS_ALLOWED_ORIGINS = [
    origin.strip()
    for origin in os.environ.get(
        'CORS_ALLOWED_ORIGINS',
        'http://localhost:5173,http://localhost:3000'
    ).split(',')
    if origin.strip()
]
CORS_ALLOWED_ORIGIN_REGEXES = []
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_ALL_ORIGINS = DEBUG

CSRF_TRUSTED_ORIGINS = [
    origin.strip()
    for origin in os.environ.get('CSRF_TRUSTED_ORIGINS', '').split(',')
    if origin.strip()
]

# Data Directory
DATA_DIR = Path(os.environ.get('DATA_DIR', BASE_DIR.parent / "data"))

# Crawler Config
CRAWLER_CONFIG = {
    "platforms": ["xhs", "dy", "ks", "bili", "wb", "tieba", "zhihu"],
    "login_types": ["qrcode", "cookie", "phone"],
    "crawler_types": ["search", "detail", "creator"],
    "save_options": ["json", "csv", "excel", "db", "mongodb"],
    "default_platform": os.environ.get('CRAWLER_PLATFORM', 'xhs'),
    "default_login_type": os.environ.get('CRAWLER_LOGIN_TYPE', 'qrcode'),
    "default_crawler_type": os.environ.get('CRAWLER_TYPE', 'search'),
    "default_keywords": os.environ.get('CRAWLER_KEYWORDS', '').split(','),
    "save_data_option": os.environ.get('SAVE_DATA_OPTION', 'db'),
}

# Server
SERVER_HOST = os.environ.get('HOST', '0.0.0.0')
SERVER_PORT = int(os.environ.get('PORT', 8000))

# Logging
LOG_LEVEL = os.environ.get('DJANGO_LOG_LEVEL', 'INFO')
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": BASE_DIR / "logs" / "django.log",
            "maxBytes": 1024 * 1024 * 10,
            "backupCount": 5,
            "formatter": "verbose",
        },
    },
    "root": {
        "handlers": ["console", "file"],
        "level": LOG_LEVEL,
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": LOG_LEVEL,
            "propagate": False,
        },
        "api": {
            "handlers": ["console", "file"],
            "level": "INFO",
            "propagate": False,
        },
    },
}

# Create logs directory
(BASE_DIR / "logs").mkdir(exist_ok=True)
