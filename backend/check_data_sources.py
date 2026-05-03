#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import os
from pathlib import Path

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mediacrawler_config.settings")

import django

django.setup()

from django.test import Client

from api import views as api_views


ROOT = Path(__file__).resolve().parent
CRAWLER_MEDIA_PLATFORM_DIR = ROOT / "crawler" / "media_platform"

PLATFORM_MODULE_FILES = {
    "xhs": ["core.py", "login.py", "client.py", "field.py"],
    "dy": ["core.py", "login.py", "client.py", "help.py"],
    "ks": ["core.py", "login.py", "client.py"],
    "bili": ["core.py", "login.py", "client.py"],
    "wb": ["core.py", "login.py", "client.py"],
    "tieba": ["core.py", "login.py", "client.py"],
    "zhihu": ["core.py", "login.py", "client.py"],
}


def _ok(name: str, details):
    return {"name": name, "ok": True, "details": details}


def _fail(name: str, details):
    return {"name": name, "ok": False, "details": details}


def _run_endpoint_checks():
    client = Client(HTTP_HOST="127.0.0.1")
    checks = []

    health = client.get("/api/health")
    checks.append(
        _ok("/api/health", health.json()) if health.status_code == 200 else _fail("/api/health", health.status_code)
    )

    platforms = client.get("/api/config/platforms")
    checks.append(
        _ok("/api/config/platforms", platforms.json()) if platforms.status_code == 200 else _fail("/api/config/platforms", platforms.status_code)
    )

    options = client.get("/api/config/options")
    checks.append(
        _ok("/api/config/options", {"status": options.status_code}) if options.status_code == 200 else _fail("/api/config/options", options.status_code)
    )

    crawler_status = client.get("/api/crawler/status")
    checks.append(
        _ok("/api/crawler/status", crawler_status.json()) if crawler_status.status_code == 200 else _fail("/api/crawler/status", crawler_status.status_code)
    )

    data_stats = client.get("/api/data/stats")
    checks.append(
        _ok("/api/data/stats", data_stats.json()) if data_stats.status_code == 200 else _fail("/api/data/stats", data_stats.status_code)
    )

    sentiment_stats = client.get("/api/monitor/platform-sentiment-stats")
    checks.append(
        _ok("/api/monitor/platform-sentiment-stats", {"status": sentiment_stats.status_code})
        if sentiment_stats.status_code == 200
        else _fail("/api/monitor/platform-sentiment-stats", sentiment_stats.status_code)
    )

    for platform in api_views.PLATFORM_NAMES:
        sensitive = client.get("/api/monitor/feed/sensitive", {"platform": platform, "page": 1, "page_size": 5})
        all_feed = client.get("/api/monitor/feed/all", {"platform": platform, "page": 1, "page_size": 5})
        qr = client.get(f"/api/login/qr/{platform}")
        qr_status = client.get(f"/api/login/qr/{platform}/status")
        checks.append(
            _ok(f"{platform}:sensitive_feed", {"status": sensitive.status_code})
            if sensitive.status_code == 200
            else _fail(f"{platform}:sensitive_feed", sensitive.status_code)
        )
        checks.append(
            _ok(f"{platform}:all_feed", {"status": all_feed.status_code})
            if all_feed.status_code == 200
            else _fail(f"{platform}:all_feed", all_feed.status_code)
        )
        checks.append(
            _ok(f"{platform}:login_qr", qr.json()) if qr.status_code == 200 else _fail(f"{platform}:login_qr", qr.status_code)
        )
        checks.append(
            _ok(f"{platform}:login_qr_status", qr_status.json())
            if qr_status.status_code == 200
            else _fail(f"{platform}:login_qr_status", qr_status.status_code)
        )

    invalid_qr = client.get("/api/login/qr/invalid-platform")
    checks.append(
        _ok("invalid-platform-rejected", {"status": invalid_qr.status_code})
        if invalid_qr.status_code == 400
        else _fail("invalid-platform-rejected", {"status": invalid_qr.status_code})
    )

    return checks


def _run_platform_config_checks():
    checks = []
    platform_keys = set(api_views.PLATFORM_NAMES.keys())

    checks.append(
        _ok(
            "platform-config-key-consistency",
            {
                "aliases": sorted(api_views.PLATFORM_PATH_ALIASES.keys()),
                "names": sorted(api_views.PLATFORM_NAMES.keys()),
                "feed_config": sorted(api_views.PLATFORM_FEED_CONFIG.keys()),
                "url_fields": sorted(api_views.PLATFORM_URL_FIELDS.keys()),
                "qr_platforms": sorted(api_views.SUPPORTED_QR_PLATFORMS),
            },
        )
        if platform_keys
        == set(api_views.PLATFORM_PATH_ALIASES.keys())
        == set(api_views.PLATFORM_FEED_CONFIG.keys())
        == set(api_views.PLATFORM_URL_FIELDS.keys())
        == set(api_views.SUPPORTED_QR_PLATFORMS)
        else _fail("platform-config-key-consistency", "Platform config key mismatch")
    )

    for platform in sorted(platform_keys):
        feed_config = api_views.PLATFORM_FEED_CONFIG[platform]
        model = feed_config["model"]
        missing_attrs = [
            attr
            for attr in [feed_config["id_field"], feed_config["time_field"], feed_config["author_field"], *feed_config["content_fields"]]
            if not hasattr(model, attr)
        ]
        checks.append(
            _ok(f"{platform}:model-fields", {"model": model.__name__})
            if not missing_attrs
            else _fail(f"{platform}:model-fields", {"model": model.__name__, "missing_attrs": missing_attrs})
        )

        missing_files = []
        module_dir_name = {
            "xhs": "xhs",
            "dy": "douyin",
            "ks": "kuaishou",
            "bili": "bilibili",
            "wb": "weibo",
            "tieba": "tieba",
            "zhihu": "zhihu",
        }[platform]
        for relative_name in PLATFORM_MODULE_FILES[platform]:
            candidate = CRAWLER_MEDIA_PLATFORM_DIR / module_dir_name / relative_name
            if not candidate.exists():
                missing_files.append(str(candidate.relative_to(ROOT)))
        checks.append(
            _ok(f"{platform}:crawler-module-files", {"module_dir": module_dir_name})
            if not missing_files
            else _fail(f"{platform}:crawler-module-files", {"missing_files": missing_files})
        )

    return checks


def main():
    endpoint_checks = _run_endpoint_checks()
    config_checks = _run_platform_config_checks()
    checks = endpoint_checks + config_checks
    failures = [item for item in checks if not item["ok"]]

    summary = {
        "total_checks": len(checks),
        "passed": len(checks) - len(failures),
        "failed": len(failures),
        "checks": checks,
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    raise SystemExit(1 if failures else 0)


if __name__ == "__main__":
    main()
