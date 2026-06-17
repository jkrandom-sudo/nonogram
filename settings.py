"""Persistent settings."""
import json
from pathlib import Path
from typing import Optional


DEFAULT_PATH = Path.home() / ".nonogram_settings.json"

DEFAULTS = {
    "lang": "zh",
    "sound": True,
    "volume": 1,
    "size": 5,
}

VALID_LANGS = ("zh", "en")
VALID_SIZES = (5, 10)


def load(path: Optional[Path] = None) -> dict:
    if path is None:
        path = DEFAULT_PATH
    s = dict(DEFAULTS)
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, dict):
            for k, v in data.items():
                if k in s:
                    s[k] = v
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        pass
    if s.get("lang") not in VALID_LANGS:
        s["lang"] = DEFAULTS["lang"]
    if not isinstance(s.get("sound"), bool):
        s["sound"] = DEFAULTS["sound"]
    if not isinstance(s.get("volume"), int) or s["volume"] < 0 or s["volume"] > 3:
        s["volume"] = DEFAULTS["volume"]
    if s.get("size") not in VALID_SIZES:
        s["size"] = DEFAULTS["size"]
    return s


def save(s: dict, path: Optional[Path] = None) -> None:
    if path is None:
        path = DEFAULT_PATH
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(s, f, indent=2, ensure_ascii=False)
    except OSError:
        pass


def cycle_lang(s: dict) -> dict:
    s["lang"] = "en" if s.get("lang") == "zh" else "zh"
    return s


def toggle_sound(s: dict) -> dict:
    s["sound"] = not bool(s.get("sound", True))
    return s


def cycle_volume(s: dict) -> dict:
    s["volume"] = (s.get("volume", 1) + 1) % 4
    return s


def cycle_size(s: dict) -> dict:
    cur = s.get("size", 5)
    idx = VALID_SIZES.index(cur) if cur in VALID_SIZES else 0
    s["size"] = VALID_SIZES[(idx + 1) % len(VALID_SIZES)]
    return s
