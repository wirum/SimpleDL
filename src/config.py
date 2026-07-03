"""Project configuration for SimpleDL.

Loads settings from config.yml (created from config.example.yml if missing)
and exposes them as a simple in-memory dict that the rest of the app reads
and writes directly.

Public contract expected by cli.py and downloader.py:
  - CONFIG: dict with the current settings
  - CONFIG_PATH: Path to the config.yml file in use
  - save_config(): persists CONFIG back to CONFIG_PATH
"""
from pathlib import Path
from typing import Any, Dict

try:
    import yaml
except ImportError:
    yaml = None


# config.py lives in src/. config.yml belongs at the project root (one
# level up), alongside config.example.yml, requirements.txt, etc.
CONFIG_PATH = Path(__file__).resolve().parent.parent / "config.yml"

# Defaults used when config.yml doesn't exist yet or a key is missing.
# These mirror what cli.py already falls back to via CONFIG.get(key, default).
_DEFAULTS: Dict[str, Any] = {
    "default_out_dir": "./downloads",
    "default_format": "mp4",
    "default_quality": "best",
    "log_path": "./logs/downloads.log",
    "verbosity": "info",
    "remote_components": None,
}

CONFIG: Dict[str, Any] = {}


def _load() -> None:
    """Load CONFIG from CONFIG_PATH, falling back to defaults for missing keys."""
    global CONFIG
    data: Dict[str, Any] = {}
    if CONFIG_PATH.exists() and yaml is not None:
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                loaded = yaml.safe_load(f)
                if isinstance(loaded, dict):
                    data = loaded
        except Exception:
            # If config.yml is malformed, fall back to defaults rather than crash.
            data = {}
    merged = dict(_DEFAULTS)
    merged.update(data)
    CONFIG = merged


def save_config() -> None:
    """Write the current CONFIG dict back to CONFIG_PATH as YAML."""
    if yaml is None:
        raise RuntimeError("pyyaml is required to save config.yml. Install with: pip install pyyaml")
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        yaml.safe_dump(CONFIG, f, default_flow_style=False, sort_keys=True)


_load()
