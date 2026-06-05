import sys
import types
import uuid
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
from unittest.mock import patch

import pytest
from django.core.exceptions import ImproperlyConfigured


SETTINGS_PATH = Path(__file__).resolve().parents[1] / "mediacrawler_config" / "settings.py"
ENV_PATH = SETTINGS_PATH.parent.parent / ".env"

DATABASE_ENV_KEYS = [
    "DB_ENGINE",
    "DB_NAME",
    "DB_USER",
    "DB_PASSWORD",
    "DB_HOST",
    "DB_PORT",
    "MYSQL_DB_NAME",
    "MYSQL_DB_USER",
    "MYSQL_DB_PASSWORD",
    "MYSQL_DB_PWD",
    "MYSQL_DB_HOST",
    "MYSQL_DB_PORT",
    "POSTGRES_DB_NAME",
    "POSTGRES_DB_USER",
    "POSTGRES_DB_PASSWORD",
    "POSTGRES_DB_PWD",
    "POSTGRES_DB_HOST",
    "POSTGRES_DB_PORT",
]


def load_settings(monkeypatch, env=None, env_file_exists=False, stub_pymysql=False):
    env = env or {}
    for key in DATABASE_ENV_KEYS:
        monkeypatch.delenv(key, raising=False)
    for key, value in env.items():
        monkeypatch.setenv(key, value)

    module_name = f"test_settings_{uuid.uuid4().hex}"
    spec = spec_from_file_location(module_name, SETTINGS_PATH)
    module = module_from_spec(spec)

    original_exists = Path.exists
    fake_modules = {}
    if stub_pymysql:
        fake_pymysql = types.ModuleType("pymysql")
        fake_pymysql.install_as_MySQLdb = lambda: None
        fake_modules["pymysql"] = fake_pymysql

    def fake_exists(path_obj):
        if path_obj == ENV_PATH:
            return env_file_exists
        return original_exists(path_obj)

    with patch("pathlib.Path.exists", fake_exists), patch("dotenv.load_dotenv"), patch.dict(
        sys.modules, fake_modules, clear=False
    ):
        sys.modules[module_name] = module
        try:
            spec.loader.exec_module(module)
        finally:
            sys.modules.pop(module_name, None)

    return module


def test_defaults_to_local_mysql_when_env_file_is_missing(monkeypatch):
    settings = load_settings(monkeypatch, env_file_exists=False, stub_pymysql=True)

    assert settings.DB_ENGINE == "mysql"
    assert settings.DATABASES["default"]["ENGINE"] == "django.db.backends.mysql"
    assert settings.DATABASES["default"]["NAME"] == "media_crawler"
    assert settings.DATABASES["default"]["USER"] == "root"
    assert settings.DATABASES["default"]["PASSWORD"] == ""
    assert settings.DATABASES["default"]["HOST"] == "localhost"
    assert settings.DATABASES["default"]["PORT"] == "3306"


def test_supports_postgresql_alias_and_compatibility_env_names(monkeypatch):
    settings = load_settings(
        monkeypatch,
        env={
            "DB_ENGINE": "postgres",
            "POSTGRES_DB_NAME": "media_crawler",
            "POSTGRES_DB_USER": "postgres",
            "POSTGRES_DB_PWD": "secret",
        },
        env_file_exists=False,
    )

    assert settings.DB_ENGINE == "postgresql"
    assert settings.DATABASES["default"]["ENGINE"] == "django.db.backends.postgresql"
    assert settings.DATABASES["default"]["NAME"] == "media_crawler"
    assert settings.DATABASES["default"]["USER"] == "postgres"
    assert settings.DATABASES["default"]["PASSWORD"] == "secret"
    assert settings.DATABASES["default"]["HOST"] == "localhost"
    assert settings.DATABASES["default"]["PORT"] == "5432"


def test_supports_mysql_when_selected_explicitly(monkeypatch):
    settings = load_settings(
        monkeypatch,
        env={
            "DB_ENGINE": "mysql",
            "DB_NAME": "media_crawler",
            "DB_USER": "root",
            "DB_PASSWORD": "secret",
            "DB_HOST": "127.0.0.1",
            "DB_PORT": "3307",
        },
        env_file_exists=False,
        stub_pymysql=True,
    )

    assert settings.DB_ENGINE == "mysql"
    assert settings.DATABASES["default"]["ENGINE"] == "django.db.backends.mysql"
    assert settings.DATABASES["default"]["NAME"] == "media_crawler"
    assert settings.DATABASES["default"]["USER"] == "root"
    assert settings.DATABASES["default"]["PASSWORD"] == "secret"
    assert settings.DATABASES["default"]["HOST"] == "127.0.0.1"
    assert settings.DATABASES["default"]["PORT"] == "3307"


def test_rejects_unsupported_database_engines(monkeypatch):
    with pytest.raises(ImproperlyConfigured, match="Unsupported DB_ENGINE"):
        load_settings(
            monkeypatch,
            env={"DB_ENGINE": "oracle"},
            env_file_exists=False,
        )
