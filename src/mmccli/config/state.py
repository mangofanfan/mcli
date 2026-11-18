# mmccli.config.state
import os
from pathlib import Path

from pydantic import BaseModel, Field

from .config_item import McliConfig_LogLevel

__all__ = [
    "McliConfig",
    "useMcliContext",
]


class McliConfig(BaseModel):
    log_level: McliConfig_LogLevel = Field(alias="log-level", default=McliConfig_LogLevel.INFO)
    no_proxy: bool = Field(alias="no-proxy", default=True)
    no_ssl_verify: bool = Field(alias="no-ssl-verify", default=True)
    editor: str = Field(alias="editor", default="#default")
    minecraft_version_manifest_v2_json: str = Field(
        alias="minecraft-version-manifest-v2-json",
        default="https://launchermeta.mojang.com/mc/game/version_manifest_v2.json",
    )
    minecraft_download_libraries_url: str = Field(
        alias="minecraft-download-libraries-url",
        default="https://libraries.minecraft.net/",
    )
    minecraft_download_assets_url: str = Field(
        alias="minecraft-download-assets-url",
        default="https://resources.download.minecraft.net/",
    )
    minecraft_download_versions_url: str = Field(
        alias="minecraft-download-versions-url",
        default="https://piston-data.mojang.com/",
    )
    forge_download_libraries_url: str = Field(
        alias="forge-download-libraries-url",
        default="https://maven.minecraftforge.net/",
    )
    fabric_download_libraries_url: str = Field(
        alias="fabric-download-libraries-url",
        default="https://maven.fabricmc.net/",
    )


class McliContext(BaseModel):
    config_dir: Path = Field(default=Path("~/.config/mmccli").expanduser())
    mmccli_dir: Path = Field(default=Path("~/.mmccli").expanduser())


def _get_path_from_env_else_none(env_var: str):
    if env_var in os.environ:
        return Path(os.environ[env_var])
    return None


context_paths = {
    "config_dir": _get_path_from_env_else_none("MCLI_CONTEXT_CONFIG_DIR"),
    "mmccli_dir": _get_path_from_env_else_none("MCLI_CONTEXT_MMCCLI_DIR"),
}

useMcliContext = McliContext(**{name: path for name, path in context_paths.items() if path is not None})
