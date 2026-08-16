"""Build an ad-hoc signed Apple Silicon app and DMG through py2app."""
from __future__ import annotations

import hashlib
import json
import platform
import shutil
import subprocess
import sys
from pathlib import Path

from app_version import APP_VERSION


ROOT = Path(__file__).parent
DIST = ROOT / "dist"
APP_NAME = "Codex Enhanced Manager.app"
DMG_NAME = f"CodexEnhancedManager-{APP_VERSION}-macos-arm64.dmg"


def run(*argv: str) -> None:
    subprocess.run(list(argv), cwd=ROOT, check=True)


def create_icon() -> None:
    iconset = ROOT / "build" / "CodexEnhancedManager.iconset"
    if iconset.exists():
        shutil.rmtree(iconset)
    iconset.mkdir(parents=True)
    sizes = ((16, "16x16"), (32, "16x16@2x"), (32, "32x32"), (64, "32x32@2x"), (128, "128x128"), (256, "128x128@2x"), (256, "256x256"), (512, "256x256@2x"), (512, "512x512"), (1024, "512x512@2x"))
    for pixels, label in sizes:
        run("sips", "-z", str(pixels), str(pixels), "icon.png", "--out", str(iconset / f"icon_{label}.png"))
    run("iconutil", "-c", "icns", str(iconset), "-o", "icon.icns")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> None:
    if platform.system() != "Darwin" or platform.machine().lower() not in {"arm64", "aarch64"}:
        raise RuntimeError("The macOS release package must be built on an Apple Silicon runner.")
    create_icon()
    run(sys.executable, "setup_macos.py", "py2app")
    app_path = DIST / APP_NAME
    run("codesign", "--force", "--deep", "--sign", "-", str(app_path))
    staging = ROOT / "build" / "dmg"
    if staging.exists():
        shutil.rmtree(staging)
    staging.mkdir(parents=True)
    shutil.copytree(app_path, staging / APP_NAME)
    (staging / "Applications").symlink_to("/Applications")
    dmg_path = DIST / DMG_NAME
    dmg_path.unlink(missing_ok=True)
    run("hdiutil", "create", "-volname", "Codex Enhanced Manager", "-srcfolder", str(staging), "-ov", "-format", "UDZO", str(dmg_path))
    manifest = {
        "name": dmg_path.name,
        "size_bytes": dmg_path.stat().st_size,
        "sha256": sha256(dmg_path),
        "architecture": "arm64",
        "minimum_macos": "12.0",
        "signing": "ad-hoc",
        "notarized": False,
        "verification": "Metadata only; the app and DMG were not launched.",
    }
    (DIST / "macos-release-manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
