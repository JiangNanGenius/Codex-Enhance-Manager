"""Recoverable batch session operations for the desktop API."""
from __future__ import annotations

import json
import shutil
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from app_paths import app_data_path, ensure_app_dirs, is_within


DELETE_CONFIRMATION = "DELETE_SELECTED_SESSIONS"


class SessionOperationManager:
    def __init__(self, db, backup_root: Path | None = None, rollout_resolver=None):
        ensure_app_dirs()
        self.db = db
        self.backup_root = Path(backup_root) if backup_root else app_data_path("backups", "session-deletions")
        self.backup_root.mkdir(parents=True, exist_ok=True)
        self.rollout_resolver = rollout_resolver

    def delete_selected(self, session_ids: list[str], confirmation: str) -> dict[str, Any]:
        ids = list(dict.fromkeys(str(item).strip() for item in session_ids if str(item).strip()))
        if confirmation != DELETE_CONFIRMATION:
            raise ValueError(f"Batch deletion requires confirmation {DELETE_CONFIRMATION!r}.")
        if not ids or len(ids) > 500:
            raise ValueError("Select between 1 and 500 sessions.")
        operation_id = f"delete-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}-{uuid.uuid4().hex[:8]}"
        operation_dir = self.backup_root / operation_id
        operation_dir.mkdir(parents=True, exist_ok=False)
        records: list[dict[str, Any]] = []
        failed: list[dict[str, str]] = []
        for session_id in ids:
            thread = self.db.get_thread(session_id)
            if not thread:
                failed.append({"id": session_id, "error": "Session not found."})
                continue
            rollout_path = Path(str(thread.get("rollout_path") or "")).expanduser()
            if not rollout_path.is_file() and self.rollout_resolver:
                resolved = str(self.rollout_resolver(thread) or "").strip()
                if resolved:
                    rollout_path = Path(resolved).expanduser()
                    thread["rollout_path"] = str(rollout_path)
            backup_file = ""
            if rollout_path.is_file():
                target = operation_dir / "rollouts" / f"{session_id}.jsonl"
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(rollout_path, target)
                backup_file = str(target.relative_to(operation_dir))
            records.append({"thread": thread, "rollout_backup": backup_file})
        manifest = {
            "operation_id": operation_id,
            "created_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "records": records,
            "failed_before_delete": failed,
        }
        manifest_path = operation_dir / "manifest.json"
        manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        deleted: list[str] = []
        for record in records:
            session_id = str(record["thread"].get("id") or "")
            if self.db.delete_thread(session_id):
                rollout_path = Path(str(record["thread"].get("rollout_path") or "")).expanduser()
                try:
                    if record.get("rollout_backup") and rollout_path.is_file():
                        rollout_path.unlink()
                    deleted.append(session_id)
                except OSError as exc:
                    self.db.restore_thread(record["thread"])
                    failed.append({"id": session_id, "error": f"Rollout deletion failed and database row was restored: {exc}"})
            else:
                failed.append({"id": session_id, "error": "Database deletion failed."})
        manifest["deleted"] = deleted
        manifest["failed"] = failed
        manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        return {
            "success": not failed,
            "operation_id": operation_id,
            "deleted": deleted,
            "failed": failed,
            "undo_available": bool(deleted),
        }

    def undo(self, operation_id: str) -> dict[str, Any]:
        safe_id = str(operation_id or "").strip()
        operation_dir = self.backup_root / safe_id
        if not safe_id or not is_within(operation_dir, self.backup_root):
            raise ValueError("Invalid session operation ID.")
        manifest_path = operation_dir / "manifest.json"
        if not manifest_path.is_file():
            raise ValueError("Session deletion backup was not found.")
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        deleted = set(str(item) for item in manifest.get("deleted", []))
        restored: list[str] = []
        failed: list[dict[str, str]] = []
        for record in manifest.get("records", []):
            thread = record.get("thread") if isinstance(record, dict) else None
            session_id = str((thread or {}).get("id") or "")
            if not session_id or session_id not in deleted:
                continue
            if not self.db.restore_thread(thread):
                failed.append({"id": session_id, "error": "Database restore failed."})
                continue
            backup_relative = str(record.get("rollout_backup") or "")
            original = Path(str(thread.get("rollout_path") or "")).expanduser()
            backup = operation_dir / backup_relative if backup_relative else None
            try:
                if backup and backup.is_file() and is_within(backup, operation_dir) and not original.exists():
                    original.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(backup, original)
                restored.append(session_id)
            except OSError as exc:
                failed.append({"id": session_id, "error": f"Rollout restore failed: {exc}"})
        manifest["restored"] = restored
        manifest["restore_failed"] = failed
        manifest["restored_at"] = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        return {"success": not failed, "operation_id": safe_id, "restored": restored, "failed": failed}
