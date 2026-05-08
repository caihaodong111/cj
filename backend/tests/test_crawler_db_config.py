import sys
import uuid
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path


DB_CONFIG_PATH = Path(__file__).resolve().parents[1] / "crawler" / "config" / "db_config.py"

DB_ENV_KEYS = [
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


def load_db_config(monkeypatch):
    for key in DB_ENV_KEYS:
        monkeypatch.delenv(key, raising=False)

    module_name = f"test_db_config_{uuid.uuid4().hex}"
    spec = spec_from_file_location(module_name, DB_CONFIG_PATH)
    module = module_from_spec(spec)
    sys.modules[module_name] = module
    try:
        spec.loader.exec_module(module)
    finally:
        sys.modules.pop(module_name, None)
    return module


def test_crawler_database_defaults_are_local_only(monkeypatch):
    db_config = load_db_config(monkeypatch)

    assert db_config.mysql_db_config["host"] == "localhost"
    assert db_config.mysql_db_config["db_name"] == "media_crawler"
    assert db_config.mysql_db_config["user"] == "root"

    assert db_config.postgres_db_config["host"] == "localhost"
    assert db_config.postgres_db_config["db_name"] == "media_crawler"
    assert db_config.postgres_db_config["user"] == "postgres"
