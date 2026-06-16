"""
app_paths.py - Local storage paths for Codex Enhanced Manager.

User data defaults to the user's Documents folder instead of Program Files or
the executable directory. This keeps the app portable and makes cleanup/export
boundaries explicit.
"""
from __future__ import annotations

import os
import shutil
from pathlib import Path
from typing import Iterable


APP_DIR_NAME = "Codex Enhanced Manager"
LEGACY_APP_DIR_NAMES = ("Codex Enhance Manager",)
LEGACY_CONFIG_FILE = Path.home() / ".codex_gui_config.json"
LEGACY_APP_DIR = Path.home() / ".codex_enhance_manager"
ZH_DOCUMENTS_DIR = "\u6587\u6863"


def user_documents_dir() -> Path:
    """Best-effort Windows Documents folder detection with OneDrive support."""
    candidates = []
    for env_name in ("OneDriveCommercial", "OneDriveConsumer", "OneDrive"):
        base = os.environ.get(env_name)
        if base:
            candidates.extend([Path(base) / ZH_DOCUMENTS_DIR, Path(base) / "Documents"])
    candidates.extend([Path.home() / "OneDrive" / ZH_DOCUMENTS_DIR, Path.home() / "OneDrive" / "Documents"])
    candidates.extend([Path.home() / ZH_DOCUMENTS_DIR, Path.home() / "Documents"])

    for candidate in candidates:
        try:
            if candidate.exists() and candidate.is_dir():
                return candidate
        except OSError:
            continue
    return Path.home()


def app_data_dir() -> Path:
    return user_documents_dir() / APP_DIR_NAME


def legacy_app_data_dirs() -> list[Path]:
    documents = user_documents_dir()
    current = app_data_dir()
    result: list[Path] = []
    seen: set[Path] = set()
    for name in LEGACY_APP_DIR_NAMES:
        candidate = documents / name
        try:
            resolved = candidate.resolve()
        except OSError:
            resolved = candidate
        if candidate == current or resolved in seen:
            continue
        seen.add(resolved)
        result.append(candidate)
    return result


def migrate_legacy_app_data_dir() -> None:
    target = app_data_dir()
    if target.exists():
        return
    for legacy_dir in legacy_app_data_dirs():
        try:
            if legacy_dir.exists() and legacy_dir.is_dir():
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copytree(legacy_dir, target)
                return
        except OSError:
            continue


def app_data_path(*parts: str) -> Path:
    path = app_data_dir()
    for part in parts:
        path = path / part
    return path


def ensure_app_dirs(extra_dirs: Iterable[Path] = ()) -> None:
    migrate_legacy_app_data_dir()
    dirs = [
        app_data_dir(),
        app_data_path("backups"),
        app_data_path("codex_backups"),
        app_data_path("diagnostics"),
        app_data_path("exports"),
        app_data_path("logs"),
        app_data_path("temp"),
        app_data_path("providers"),
    ]
    dirs.extend(extra_dirs)
    for directory in dirs:
        directory.mkdir(parents=True, exist_ok=True)


def is_within(path: Path, root: Path) -> bool:
    """Return True when path resolves inside root."""
    try:
        path.resolve().relative_to(root.resolve())
        return True
    except (OSError, ValueError):
        return False
