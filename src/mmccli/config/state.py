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


useMcliConfig = McliConfig()
