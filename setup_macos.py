"""py2app configuration for the Apple Silicon desktop bundle."""
from pathlib import Path

from setuptools import setup

from app_version import APP_VERSION


ROOT = Path(__file__).parent

setup(
    app=["main.py"],
    name="Codex Enhanced Manager",
    version=APP_VERSION.lstrip("v"),
    data_files=(
        [(str(path.parent.relative_to(ROOT)), [str(path)]) for path in (ROOT / "static").rglob("*") if path.is_file()]
        + [("", ["icon.png", "icon.ico", "LICENSE", "README.md", "README.zh-CN.md"])]
    ),
    options={
        "py2app": {
            "argv_emulation": False,
            "arch": "arm64",
            "iconfile": "icon.icns",
            "packages": ["flask", "webview", "pystray", "PIL"],
            "plist": {
                "CFBundleIdentifier": "com.jiangnangenius.codex-enhanced-manager",
                "CFBundleDisplayName": "Codex Enhanced Manager",
                "CFBundleShortVersionString": APP_VERSION.lstrip("v"),
                "CFBundleVersion": APP_VERSION.lstrip("v"),
                "LSMinimumSystemVersion": "12.0",
                "LSArchitecturePriority": ["arm64"],
                "NSHighResolutionCapable": True,
            },
        }
    },
    setup_requires=["py2app"],
)
