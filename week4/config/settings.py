import json
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[1]

SETTINGS_PATH = BASE_DIR / "config" / "settings.json"
RELATIONSHIP_MAP_PATH = BASE_DIR / "config" / "relationship_map.json"
KILL_SWITCH_PATH = BASE_DIR / "kill_switch.flag"


DEFAULT_SETTINGS = {
    "dry_run": True,
    "min_delay_seconds": 3,
    "max_delay_seconds": 12,
}


def load_settings() -> dict:
    try:
        with SETTINGS_PATH.open("r", encoding="utf-8") as f:
            data = json.load(f)

        if not isinstance(data, dict):
            return DEFAULT_SETTINGS.copy()

        settings = DEFAULT_SETTINGS.copy()
        settings.update(data)
        return settings

    except (FileNotFoundError, json.JSONDecodeError, OSError, TypeError):
        return DEFAULT_SETTINGS.copy()


def is_dry_run() -> bool:
    return bool(load_settings().get("dry_run", True))


def is_kill_switch_active() -> bool:
    return KILL_SWITCH_PATH.exists()


def get_allowlist() -> set[str]:
    try:
        with RELATIONSHIP_MAP_PATH.open("r", encoding="utf-8") as f:
            data = json.load(f)

    except (FileNotFoundError, json.JSONDecodeError, OSError, TypeError):
        return set()

    return {
        str(jid)
        for jid, relationship in data.items()
        if jid != "_default"
        and relationship != "unknown"
    }


def enforce_allowlist(jid: str) -> bool:
    number = jid.split("@", 1)[0] if jid else ""
    return number in get_allowlist()