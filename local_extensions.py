"""Local-only Codex renderer scripts, themes, and pet asset management."""
from __future__ import annotations

import hashlib
import json
import re
import shutil
import tempfile
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

from app_paths import app_data_path, ensure_app_dirs, is_within


SCRIPT_SUFFIXES = {".js"}
THEME_SUFFIXES = {".css", ".json", ".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg"}
MAX_SCRIPT_BYTES = 2 * 1024 * 1024
MAX_THEME_FILE_BYTES = 25 * 1024 * 1024
MAX_THEME_TOTAL_BYTES = 150 * 1024 * 1024
DELETE_CONFIRMATION = "DELETE_LOCAL_EXTENSION"


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _safe_id(value: str, fallback: str = "extension") -> str:
    normalized = re.sub(r"[^a-z0-9._-]+", "-", str(value or "").strip().lower())
    return normalized.strip(".-")[:80] or fallback


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _atomic_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


class LocalExtensionManager:
    def __init__(self, root: Path | None = None):
        ensure_app_dirs()
        self.root = Path(root) if root else app_data_path("extensions")
        self.scripts_dir = self.root / "scripts"
        self.themes_dir = self.root / "themes"
        self.pets_dir = self.root / "pets"
        self.registry_path = self.root / "registry.json"
        for directory in (self.scripts_dir, self.themes_dir, self.pets_dir):
            directory.mkdir(parents=True, exist_ok=True)

    def _registry(self) -> dict[str, list[dict[str, Any]]]:
        default = {"scripts": [], "themes": [], "pets": []}
        try:
            loaded = json.loads(self.registry_path.read_text(encoding="utf-8"))
        except (OSError, ValueError, TypeError):
            return default
        if not isinstance(loaded, dict):
            return default
        return {
            key: [item for item in loaded.get(key, []) if isinstance(item, dict)]
            for key in default
        }

    def _save_registry(self, registry: dict[str, list[dict[str, Any]]]) -> None:
        _atomic_json(self.registry_path, registry)

    @staticmethod
    def _public(record: dict[str, Any]) -> dict[str, Any]:
        result = dict(record)
        result["path"] = str(record.get("path") or "")
        return result

    def list_scripts(self) -> list[dict[str, Any]]:
        records = self._registry()["scripts"]
        return [self._public(record) for record in records if Path(str(record.get("path") or "")).is_file()]

    def import_script(self, source: str | Path, *, name: str = "", version: str = "") -> dict[str, Any]:
        source_path = Path(source).expanduser().resolve()
        if not source_path.is_file() or source_path.suffix.lower() not in SCRIPT_SUFFIXES:
            raise ValueError("Only an existing local .js file can be imported.")
        size = source_path.stat().st_size
        if size <= 0 or size > MAX_SCRIPT_BYTES:
            raise ValueError("Script must be non-empty and no larger than 2 MiB.")
        digest = _sha256(source_path)
        extension_id = _safe_id(name or source_path.stem)
        target = self.scripts_dir / f"{extension_id}-{digest[:12]}.js"
        if not is_within(target, self.scripts_dir):
            raise ValueError("Unsafe script destination.")
        shutil.copy2(source_path, target)
        registry = self._registry()
        previous = next((item for item in registry["scripts"] if item.get("id") == extension_id), None)
        record = {
            "id": extension_id,
            "name": str(name or source_path.stem),
            "version": str(version or "local"),
            "sha256": digest,
            "enabled": bool(previous.get("enabled")) if previous else False,
            "path": str(target),
            "source_name": source_path.name,
            "size_bytes": size,
            "installed_at": _utc_now(),
        }
        registry["scripts"] = [item for item in registry["scripts"] if item.get("id") != extension_id]
        registry["scripts"].append(record)
        self._save_registry(registry)
        if previous:
            old_path = Path(str(previous.get("path") or ""))
            if old_path != target and is_within(old_path, self.scripts_dir):
                old_path.unlink(missing_ok=True)
        return self._public(record)

    def set_script_enabled(self, extension_id: str, enabled: bool) -> dict[str, Any]:
        return self._set_enabled("scripts", extension_id, enabled)

    def enabled_script_sources(self) -> list[dict[str, str]]:
        result: list[dict[str, str]] = []
        for record in self._registry()["scripts"]:
            path = Path(str(record.get("path") or ""))
            if not record.get("enabled") or not path.is_file() or not is_within(path, self.scripts_dir):
                continue
            try:
                source = path.read_text(encoding="utf-8")
            except (OSError, UnicodeError):
                continue
            if _sha256(path) != record.get("sha256"):
                continue
            result.append({"id": str(record.get("id") or "script"), "source": source})
        return result

    def list_asset_packs(self, kind: str = "themes") -> list[dict[str, Any]]:
        kind = self._asset_kind(kind)
        root = self.themes_dir if kind == "themes" else self.pets_dir
        return [
            self._public(record)
            for record in self._registry()[kind]
            if Path(str(record.get("path") or "")).is_dir()
            and is_within(Path(str(record.get("path") or "")), root)
        ]

    def import_asset_pack(self, source: str | Path, *, kind: str = "themes") -> dict[str, Any]:
        kind = self._asset_kind(kind)
        source_path = Path(source).expanduser().resolve()
        if not source_path.exists():
            raise ValueError("Local asset pack path does not exist.")
        destination_root = self.themes_dir if kind == "themes" else self.pets_dir
        with tempfile.TemporaryDirectory(prefix="cem-extension-") as temporary:
            staging = Path(temporary) / "content"
            staging.mkdir()
            if source_path.is_file():
                if source_path.suffix.lower() != ".zip":
                    raise ValueError("Asset packs must be a local directory or ZIP file.")
                self._extract_zip(source_path, staging)
            elif source_path.is_dir():
                self._copy_asset_tree(source_path, staging)
            else:
                raise ValueError("Unsupported asset pack source.")
            content_root = self._single_content_root(staging)
            manifest = self._read_pack_manifest(content_root)
            pack_id = _safe_id(str(manifest.get("id") or source_path.stem), "asset-pack")
            digest = self._tree_digest(content_root)
            target = destination_root / f"{pack_id}-{digest[:12]}"
            if not is_within(target, destination_root):
                raise ValueError("Unsafe asset pack destination.")
            if target.exists():
                shutil.rmtree(target)
            shutil.copytree(content_root, target)
        registry = self._registry()
        previous = next((item for item in registry[kind] if item.get("id") == pack_id), None)
        record = {
            "id": pack_id,
            "name": str(manifest.get("name") or source_path.stem),
            "version": str(manifest.get("version") or "local"),
            "kind": kind[:-1],
            "sha256": digest,
            "enabled": bool(previous.get("enabled")) if previous else False,
            "path": str(target),
            "installed_at": _utc_now(),
        }
        registry[kind] = [item for item in registry[kind] if item.get("id") != pack_id]
        registry[kind].append(record)
        self._save_registry(registry)
        if previous:
            old_path = Path(str(previous.get("path") or ""))
            if old_path != target and old_path.is_dir() and is_within(old_path, destination_root):
                shutil.rmtree(old_path)
        return self._public(record)

    def set_asset_pack_enabled(self, extension_id: str, enabled: bool, *, kind: str = "themes") -> dict[str, Any]:
        return self._set_enabled(self._asset_kind(kind), extension_id, enabled, exclusive=True)

    def enabled_asset_runtime(self) -> dict[str, Any]:
        runtime: dict[str, Any] = {"theme": None, "pet": None}
        registry = self._registry()
        for key, singular, suffixes in (
            ("themes", "theme", {".css"}),
            ("pets", "pet", {".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg"}),
        ):
            record = next((item for item in registry[key] if item.get("enabled")), None)
            if not record:
                continue
            root = Path(str(record.get("path") or ""))
            expected_root = self.themes_dir if key == "themes" else self.pets_dir
            if not root.is_dir() or not is_within(root, expected_root):
                continue
            preferred = [root / ("theme.css" if key == "themes" else "pet.webp")]
            candidates = preferred + sorted(
                item for item in root.rglob("*") if item.is_file() and item.suffix.lower() in suffixes
            )
            asset = next((item for item in candidates if item.is_file() and is_within(item, root)), None)
            if not asset:
                continue
            runtime[singular] = {
                "id": str(record.get("id") or ""),
                "name": str(record.get("name") or ""),
                "relative_path": asset.relative_to(root).as_posix(),
            }
        return runtime

    def resolve_asset(self, kind: str, extension_id: str, relative_path: str) -> Path:
        key = self._asset_kind(kind)
        root_base = self.themes_dir if key == "themes" else self.pets_dir
        record = next((item for item in self._registry()[key] if item.get("id") == extension_id), None)
        if not record:
            raise ValueError("Asset pack not found.")
        root = Path(str(record.get("path") or ""))
        target = root / str(relative_path or "")
        if not root.is_dir() or not is_within(root, root_base) or not target.is_file() or not is_within(target, root):
            raise ValueError("Asset path is unavailable.")
        return target

    def delete(self, extension_id: str, *, kind: str, confirmation: str) -> dict[str, Any]:
        if confirmation != DELETE_CONFIRMATION:
            raise ValueError(f"Deletion requires confirmation {DELETE_CONFIRMATION!r}.")
        registry = self._registry()
        key = "scripts" if kind == "scripts" else self._asset_kind(kind)
        root = self.scripts_dir if key == "scripts" else (self.themes_dir if key == "themes" else self.pets_dir)
        record = next((item for item in registry[key] if item.get("id") == extension_id), None)
        if not record:
            return {"success": False, "deleted": False, "error": "Extension not found."}
        target = Path(str(record.get("path") or ""))
        if not is_within(target, root):
            raise ValueError("Refusing to delete a path outside the extension directory.")
        if target.is_dir():
            shutil.rmtree(target)
        else:
            target.unlink(missing_ok=True)
        registry[key] = [item for item in registry[key] if item.get("id") != extension_id]
        self._save_registry(registry)
        return {"success": True, "deleted": True, "id": extension_id, "kind": key}

    def _set_enabled(self, key: str, extension_id: str, enabled: bool, *, exclusive: bool = False) -> dict[str, Any]:
        registry = self._registry()
        record = next((item for item in registry[key] if item.get("id") == extension_id), None)
        if not record:
            raise ValueError("Extension not found.")
        if exclusive and enabled:
            for item in registry[key]:
                item["enabled"] = item is record
        else:
            record["enabled"] = bool(enabled)
        self._save_registry(registry)
        return self._public(record)

    @staticmethod
    def _asset_kind(kind: str) -> str:
        normalized = str(kind or "themes").strip().lower()
        aliases = {"theme": "themes", "themes": "themes", "pet": "pets", "pets": "pets"}
        if normalized not in aliases:
            raise ValueError("Asset kind must be themes or pets.")
        return aliases[normalized]

    def _extract_zip(self, archive: Path, destination: Path) -> None:
        total = 0
        with zipfile.ZipFile(archive) as bundle:
            for item in bundle.infolist():
                if item.is_dir():
                    continue
                relative = Path(item.filename)
                target = destination / relative
                if relative.is_absolute() or ".." in relative.parts or not is_within(target, destination):
                    raise ValueError("Asset ZIP contains an unsafe path.")
                if Path(item.filename).suffix.lower() not in THEME_SUFFIXES:
                    raise ValueError(f"Unsupported asset type: {item.filename}")
                if item.file_size > MAX_THEME_FILE_BYTES:
                    raise ValueError(f"Asset is too large: {item.filename}")
                total += item.file_size
                if total > MAX_THEME_TOTAL_BYTES:
                    raise ValueError("Asset pack exceeds the 150 MiB limit.")
                target.parent.mkdir(parents=True, exist_ok=True)
                with bundle.open(item) as source, target.open("wb") as output:
                    shutil.copyfileobj(source, output)

    def _copy_asset_tree(self, source: Path, destination: Path) -> None:
        total = 0
        for item in source.rglob("*"):
            if item.is_symlink():
                raise ValueError("Asset packs cannot contain symbolic links.")
            if not item.is_file():
                continue
            if item.suffix.lower() not in THEME_SUFFIXES:
                raise ValueError(f"Unsupported asset type: {item.name}")
            size = item.stat().st_size
            if size > MAX_THEME_FILE_BYTES:
                raise ValueError(f"Asset is too large: {item.name}")
            total += size
            if total > MAX_THEME_TOTAL_BYTES:
                raise ValueError("Asset pack exceeds the 150 MiB limit.")
            relative = item.relative_to(source)
            target = destination / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(item, target)

    @staticmethod
    def _single_content_root(staging: Path) -> Path:
        children = [item for item in staging.iterdir() if item.name != "__MACOSX"]
        return children[0] if len(children) == 1 and children[0].is_dir() else staging

    @staticmethod
    def _read_pack_manifest(root: Path) -> dict[str, Any]:
        for name in ("theme.json", "pet.json", "manifest.json"):
            path = root / name
            if path.is_file():
                try:
                    data = json.loads(path.read_text(encoding="utf-8"))
                except (OSError, ValueError, UnicodeError) as exc:
                    raise ValueError(f"Invalid {name}: {exc}") from exc
                return data if isinstance(data, dict) else {}
        return {}

    @staticmethod
    def _tree_digest(root: Path) -> str:
        digest = hashlib.sha256()
        files: Iterable[Path] = sorted(item for item in root.rglob("*") if item.is_file())
        for item in files:
            digest.update(item.relative_to(root).as_posix().encode("utf-8"))
            digest.update(b"\0")
            digest.update(item.read_bytes())
        return digest.hexdigest()
