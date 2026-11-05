import os
import platform
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field

from .config_item import McliConfig_LogLevel


class McliConfig(BaseModel):
    log_level: McliConfig_LogLevel = Field(alias="log-level", default=McliConfig_LogLevel.INFO)
    no_proxy: bool = Field(alias="no-proxy", default=True)
    no_ssl_verify: bool = Field(alias="no-ssl-verify", default=True)
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


match platform.system():
    case "Windows":
        ENV_HOME_NAME = "USERPROFILE"
    case _:
        ENV_HOME_NAME = "HOME"
CONFIG_ROOT_DIR = Path(os.environ.get(ENV_HOME_NAME, "")) / ".config" / "mmccli"


def save_config_to_file(key: str, value: Any):
    import tomlkit

    path = CONFIG_ROOT_DIR / "mmccli.toml"
    key = key.lower()

    if path.exists():
        with open(file=path, mode="r", encoding="UTF-8") as f:
            doc = tomlkit.parse(f.read())
    else:
        doc = tomlkit.document()
        doc.add(tomlkit.comment("mmccli/mmccli.toml"))
        doc.add(tomlkit.comment("see https://mango.js.cn/docs/mcli/concept/config"))
        doc.add(tomlkit.nl())

    if key.startswith("minecraft_"):
        title = "minecraft"
        name = key.removeprefix("minecraft_").replace("_", "-")
    elif key.startswith("forge_"):
        title = "forge"
        name = key.removeprefix("forge_").replace("_", "-")
    elif key.startswith("fabric_"):
        title = "fabric"
        name = key.removeprefix("fabric_").replace("_", "-")
    else:
        title = "mcli"
        name = key.replace("_", "-")

    if title in doc:
        table: tomlkit.api.Table = doc[title]
    else:
        table = tomlkit.table()
        doc.add(title, table)
    table[name] = value

    if not path.exists():
        path.parent.mkdir(exist_ok=True, parents=True)

    with open(file=path, mode="w", encoding="UTF-8") as f:
        f.write(tomlkit.dumps(doc))


useMcliConfig = McliConfig()
