# -*- coding: utf-8 -*-

import json
import time
from pathlib import Path
from typing import Any, Dict, Optional


BRIDGE_ROOT = Path(__file__).resolve().parents[2] / "data" / "qr_bridge"


def _normalize_platform(platform: str) -> str:
    return str(platform or "").strip().lower()


def _ensure_bridge_root() -> Path:
    BRIDGE_ROOT.mkdir(parents=True, exist_ok=True)
    return BRIDGE_ROOT


def _payload_path(platform: str, kind: str) -> Path:
    normalized = _normalize_platform(platform)
    return _ensure_bridge_root() / f"{normalized}.{kind}.json"


def _write_payload(path: Path, payload: Dict[str, Any]) -> None:
    tmp_path = path.with_suffix(path.suffix + ".tmp")
    tmp_path.write_text(
        json.dumps(payload, ensure_ascii=False),
        encoding="utf-8",
    )
    tmp_path.replace(path)


def _read_payload(path: Path) -> Optional[Dict[str, Any]]:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def write_qr(platform: str, b64: str) -> None:
    normalized = _normalize_platform(platform)
    if not normalized or not b64:
        return
    _write_payload(
        _payload_path(normalized, "qr"),
        {
            "platform": normalized,
            "qr_code": b64,
            "updated_at": time.time(),
        },
    )


def write_status(platform: str, status: str) -> None:
    normalized = _normalize_platform(platform)
    status_value = str(status or "").strip().lower()
    if not normalized or not status_value:
        return
    _write_payload(
        _payload_path(normalized, "status"),
        {
            "platform": normalized,
            "status": status_value,
            "updated_at": time.time(),
        },
    )


def read_qr(platform: str) -> Optional[Dict[str, Any]]:
    normalized = _normalize_platform(platform)
    if not normalized:
        return None
    return _read_payload(_payload_path(normalized, "qr"))


def read_status(platform: str) -> Optional[Dict[str, Any]]:
    normalized = _normalize_platform(platform)
    if not normalized:
        return None
    return _read_payload(_payload_path(normalized, "status"))


def clear_platform(platform: str) -> None:
    normalized = _normalize_platform(platform)
    if not normalized:
        return
    for kind in ("qr", "status"):
        path = _payload_path(normalized, kind)
        try:
            path.unlink(missing_ok=True)
        except Exception:
            pass
