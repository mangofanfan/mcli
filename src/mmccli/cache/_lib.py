# mmccli.cache._lib

import os
import platform
import shutil
from pathlib import Path

from mmccli.log import useGlobalState

match platform.system():
    case "Windows":
        ENV_HOME_NAME = "USERPROFILE"
    case _:
        ENV_HOME_NAME = "HOME"
CACHE_ROOT_DIR = Path(os.environ.get(ENV_HOME_NAME, "")) / ".mmccli" / "cache"
CACHE_ROOT_DIR.mkdir(parents=True, exist_ok=True)


def get_library_cache_file_path(file_path: str | Path):
    return CACHE_ROOT_DIR / "libraries" / file_path


def get_assets_cache_file_path(file_path: str | Path):
    return CACHE_ROOT_DIR / "assets" / file_path


def get_version_jar_cache_file_path(file_path: str | Path):
    return CACHE_ROOT_DIR / "versions" / file_path


def get_forge_installer_cache_file_path(file_path: str | Path):
    return CACHE_ROOT_DIR / "forge-installer" / file_path


def link_or_move(cache_file_path: str | Path, file_path: str | Path):
    if useGlobalState.HARDLINK_DOWNGRADE_TO_FULL_COPY:
        shutil.copy(cache_file_path, file_path)
        return

    try:
        if Path(file_path).exists():
            os.remove(file_path)
        os.link(cache_file_path, file_path)
    except Exception:
        if not useGlobalState.HARDLINK_DOWNGRADE_TO_FULL_COPY:
            useGlobalState.HARDLINK_DOWNGRADE_TO_FULL_COPY = True
        shutil.copy(cache_file_path, file_path)
