"""Explicit local development workflow operations."""
from __future__ import annotations

import json
import os
import platform
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from app_paths import app_data_path, ensure_app_dirs, is_within


WORKTREE_CONFIRMATION = "CREATE_UPSTREAM_WORKTREE"


class WorkflowManager:
    def __init__(self, state_path: Path | None = None):
        ensure_app_dirs()
        self.state_path = Path(state_path) if state_path else app_data_path("workflows", "projects.json")

    def platform_capabilities(self) -> dict[str, Any]:
        system = platform.system()
        machine = platform.machine().lower()
        return {
            "platform": system,
            "architecture": machine,
            "windows": system == "Windows",
            "macos": system == "Darwin",
            "macos_arm64": system == "Darwin" and machine in {"arm64", "aarch64"},
            "startup": system in {"Windows", "Darwin"},
            "desktop_shortcuts": system == "Windows",
            "worktrees": bool(self._git_path()),
            "zed_remote_records": True,
            "remote_control": False,
            "wechat_bridge": False,
            "online_extension_market": False,
        }

    def preview_worktree(self, payload: dict[str, Any]) -> dict[str, Any]:
        raw_repository = str(payload.get("repository") or "").strip()
        raw_target = str(payload.get("target") or "").strip()
        repository = Path(raw_repository or ".").expanduser().resolve()
        target = Path(raw_target or ".").expanduser().resolve()
        remote = self._safe_remote(str(payload.get("remote") or "upstream"))
        base_branch = self._safe_ref(str(payload.get("base_branch") or "main"))
        branch = self._safe_ref(str(payload.get("branch") or ""))
        errors: list[str] = []
        if not self._git_path():
            errors.append("Git is not available on this platform.")
        if not raw_repository:
            errors.append("An explicit repository path is required.")
        if not raw_target:
            errors.append("An explicit target worktree path is required.")
        if not (repository / ".git").exists():
            errors.append("Repository must be an existing Git working tree.")
        if not branch:
            errors.append("A new local branch name is required.")
        if target.exists():
            errors.append("Target worktree path already exists.")
        if target == repository or is_within(target, repository / ".git"):
            errors.append("Target worktree path is unsafe.")
        commands = [
            ["git", "fetch", remote, base_branch],
            ["git", "worktree", "add", "-b", branch, str(target), f"{remote}/{base_branch}"],
        ]
        return {
            "success": not errors,
            "supported": bool(self._git_path()),
            "repository": str(repository),
            "target": str(target),
            "remote": remote,
            "base_branch": base_branch,
            "branch": branch,
            "commands": commands,
            "errors": errors,
            "required_confirmation": WORKTREE_CONFIRMATION,
        }

    def create_worktree(self, payload: dict[str, Any], confirmation: str) -> dict[str, Any]:
        preview = self.preview_worktree(payload)
        if confirmation != WORKTREE_CONFIRMATION:
            return {"success": False, "error": "Worktree confirmation required.", "preview": preview}
        if not preview["success"]:
            return {"success": False, "error": "Worktree preview is invalid.", "preview": preview}
        results = []
        for command in preview["commands"]:
            completed = subprocess.run(
                command,
                cwd=preview["repository"],
                capture_output=True,
                text=True,
                timeout=120,
                check=False,
            )
            results.append({
                "argv": command,
                "returncode": completed.returncode,
                "stdout": completed.stdout,
                "stderr": completed.stderr,
            })
            if completed.returncode != 0:
                return {"success": False, "preview": preview, "results": results}
        self.record_project({
            "kind": "worktree",
            "name": Path(preview["target"]).name,
            "path": preview["target"],
            "repository": preview["repository"],
            "branch": preview["branch"],
        })
        return {"success": True, "preview": preview, "results": results}

    def list_projects(self) -> list[dict[str, Any]]:
        state = self._read_state()
        return state.get("projects", [])

    def record_project(self, payload: dict[str, Any]) -> dict[str, Any]:
        path = str(payload.get("path") or "").strip()
        if not path:
            raise ValueError("Project path is required.")
        record = {
            "id": self._project_id(payload),
            "kind": str(payload.get("kind") or "local"),
            "name": str(payload.get("name") or Path(path).name or path),
            "path": path,
            "host": str(payload.get("host") or ""),
            "repository": str(payload.get("repository") or ""),
            "branch": str(payload.get("branch") or ""),
            "updated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        }
        state = self._read_state()
        state["projects"] = [item for item in state.get("projects", []) if item.get("id") != record["id"]]
        state["projects"].insert(0, record)
        state["projects"] = state["projects"][:100]
        self._write_state(state)
        return record

    def delete_project(self, project_id: str) -> dict[str, Any]:
        state = self._read_state()
        before = len(state.get("projects", []))
        state["projects"] = [item for item in state.get("projects", []) if item.get("id") != project_id]
        self._write_state(state)
        return {"success": len(state["projects"]) < before, "id": project_id}

    @staticmethod
    def _safe_remote(value: str) -> str:
        if not re.fullmatch(r"[A-Za-z0-9._-]+", value):
            raise ValueError("Invalid Git remote name.")
        return value

    @staticmethod
    def _safe_ref(value: str) -> str:
        value = value.strip()
        if not value:
            return ""
        if value.startswith("-") or not re.fullmatch(r"[A-Za-z0-9._/-]+", value) or ".." in value:
            raise ValueError("Invalid Git branch name.")
        return value

    @staticmethod
    def _git_path() -> str:
        from shutil import which
        return which("git") or ""

    def _read_state(self) -> dict[str, Any]:
        try:
            data = json.loads(self.state_path.read_text(encoding="utf-8"))
        except (OSError, ValueError, TypeError):
            return {"projects": []}
        return data if isinstance(data, dict) and isinstance(data.get("projects"), list) else {"projects": []}

    def _write_state(self, state: dict[str, Any]) -> None:
        self.state_path.parent.mkdir(parents=True, exist_ok=True)
        temporary = self.state_path.with_suffix(".tmp")
        temporary.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        temporary.replace(self.state_path)

    @staticmethod
    def _project_id(payload: dict[str, Any]) -> str:
        import hashlib
        raw = "\0".join(str(payload.get(key) or "") for key in ("kind", "host", "path"))
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:20]
