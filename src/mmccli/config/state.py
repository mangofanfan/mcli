from pydantic import BaseModel, Field

from .config_item import McliConfig_LogLevel


class McliConfig(BaseModel):
    log_level: McliConfig_LogLevel = Field(alias="log-level", default=McliConfig_LogLevel.INFO)
    no_proxy: bool = Field(alias="no-proxy", default=True)
    no_ssl_verify: bool = Field(alias="no-ssl-verify", default=True)
    mc_game_version_manifest_v2_json: str = Field(
        alias="mc-game-version-manifest-v2-json",
        default="https://launchermeta.mojang.com/mc/game/version_manifest_v2.json",
    )
    mc_game_download_libraries_url: str = Field(
        alias="mc-game-download-libraries-url",
        default="https://libraries.minecraft.net/",
    )
    mc_game_download_assets_url: str = Field(
        alias="mc-game-download-assets-url",
        default="https://resources.download.minecraft.net/",
    )
    mc_game_download_versions_url: str = Field(
        alias="mc-game-download-versions-url",
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
