# mmccli.app

from importlib.metadata import version

from dotenv import load_dotenv
from rich.panel import Panel

_dev_version = version("mmccli").find("dev") > 0

if _dev_version:
    load_dotenv()

from importlib import resources
from random import choice
from typing import Annotated

import typer

from mmccli.cache import app_cache
from mmccli.config import app_config, useMcliConfig
from mmccli.config.config_item import McliConfig_LogLevel
from mmccli.log import console, err, info, useGlobalState, warn
from mmccli.minecraft import app_minecraft

app = typer.Typer(help="Minecraft Java Cli", name="MCLI")
app.add_typer(app_minecraft)
app.add_typer(app_cache)
app.add_typer(app_config)


with open(file=str(resources.files("mmccli").joinpath("assets/hitokoto.txt")), mode="r", encoding="UTF-8") as f:
    line = choice(f.readlines())
console.print(f"[#748cab]MCLI >[/#748cab] [#b5c99a]{line.strip()}[/#b5c99a]")

if _dev_version:
    panel = Panel(
        "正在运行 MCLI [yellow]开发中版本[/yellow]，[red]工作区环境变量[/red]会自动加载。\n"
        "MCLI-MMCCLI [yellow]{version}[/yellow]".format(version=version("mmccli")),
        title="Dev-Version Warning",
        title_align="left",
        border_style="yellow",
    )
    console.print(panel)


def _version_callback(value: bool):
    if value:
        from mmccli import __version__

        print(f"MCLI-MMCCLI {__version__}")
        raise typer.Exit()


@app.callback()
def mmccli_main_callback(
    version: Annotated[
        bool,
        typer.Option(
            "--version",
            "-V",
            help="打印当前 MCLI 的版本号，并退出",
            callback=_version_callback,
            is_eager=True,
            rich_help_panel="Info",
        ),
    ] = False,
    log_level: Annotated[
        McliConfig_LogLevel,
        typer.Option(
            "--log-level",
            help="设置日志输出级别",
            envvar="MCLI_LOG_LEVEL",
            rich_help_panel="Config options",
        ),
    ] = McliConfig_LogLevel.INFO,
    no_proxy: Annotated[
        bool,
        typer.Option(
            "--no-proxy",
            help="布尔值，忽略环境变量中的代理设置",
            envvar="MCLI_NO_PROXY",
            rich_help_panel="Config options",
        ),
    ] = True,
    no_ssl_verify: Annotated[
        bool,
        typer.Option(
            "--no-ssl-verify",
            help="布尔值，仅在下载文件时不验证 SSL 证书",
            envvar="MCLI_NO_SSL_VERIFY",
            rich_help_panel="Config options",
        ),
    ] = True,
    mc_game_version_manifest_v2_json: Annotated[
        str,
        typer.Option(
            "--mc-game-version-manifest-v2-json",
            help="Minecraft 版本信息 URL",
            envvar="MCLI_MC_GAME_VERSION_MANIFEST_V2_JSON",
            rich_help_panel="Config options",
        ),
    ] = "https://launchermeta.mojang.com/mc/game/version_manifest_v2.json",
    mc_game_download_libraries_url: Annotated[
        str,
        typer.Option(
            "--mc-game-download-libraries-url",
            help="Minecraft 依赖库文件下载 URL",
            envvar="MCLI_MC_GAME_DOWNLOAD_LIBRARIES_URL",
            rich_help_panel="Config options",
        ),
    ] = "https://libraries.minecraft.net/",
    mc_game_download_assets_url: Annotated[
        str,
        typer.Option(
            "--mc-game-download-assets-url",
            help="Minecraft 资源文件下载 URL",
            envvar="MCLI_MC_GAME_DOWNLOAD_ASSETS_URL",
            rich_help_panel="Config options",
        ),
    ] = "https://resources.download.minecraft.net/",
    mc_game_download_versions_url: Annotated[
        str,
        typer.Option(
            "--mc-game-download-versions-url",
            help="Minecraft 本体文件下载 URL",
            envvar="MCLI_MC_GAME_DOWNLOAD_VERSIONS_URL",
            rich_help_panel="Config options",
        ),
    ] = "https://piston-data.mojang.com/",
    forge_download_libraries_url: Annotated[
        str,
        typer.Option(
            "--forge-download-libraries-url",
            help="Forge 依赖库文件下载 URL",
            envvar="MCLI_FORGE_DOWNLOAD_LIBRARIES_URL",
            rich_help_panel="Config options",
        ),
    ] = "https://maven.minecraftforge.net/",
    fabric_download_libraries_url: Annotated[
        str,
        typer.Option(
            "--fabric-download-libraries-url",
            help="Fabric 依赖库文件下载 URL",
            envvar="MCLI_FABRIC_DOWNLOAD_LIBRARIES_URL",
            rich_help_panel="Config options",
        ),
    ] = "https://maven.fabricmc.net/",
):
    useMcliConfig.log_level = log_level
    useMcliConfig.no_proxy = no_proxy
    useMcliConfig.no_ssl_verify = no_ssl_verify
    useMcliConfig.mc_game_version_manifest_v2_json = mc_game_version_manifest_v2_json
    useMcliConfig.mc_game_download_libraries_url = mc_game_download_libraries_url
    useMcliConfig.mc_game_download_assets_url = mc_game_download_assets_url
    useMcliConfig.mc_game_download_versions_url = mc_game_download_versions_url
    useMcliConfig.forge_download_libraries_url = forge_download_libraries_url
    useMcliConfig.fabric_download_libraries_url = fabric_download_libraries_url


@app.command(name="add")
def mmccli_add(
    mc_version_id: Annotated[
        str, typer.Option("--minecraft", "-mc", help="Minecraft 本体版本，或用 latest-release 和 latest-snapshot")
    ],
    forge_version_promo_or_id: Annotated[
        str | None,
        typer.Option("--forge", "-fo", help="Forge 加载器版本，或用 latest 和 recommended，不安装 forge 请省略"),
    ] = None,
    fabric_version_promo_or_id: Annotated[
        str | None,
        typer.Option("--fabric", "-fa", help="Fabric 加载器版本，或用 latest，不安装 fabric 请省略"),
    ] = None,
    name: Annotated[str | None, typer.Option("--name", "-n", help="版本的自定义名称")] = None,
):
    """
    添加一个游戏版本并立刻开始构建。
    """
    from mmccli.path_dector import detect_minecraft_install_folder

    if not detect_minecraft_install_folder():
        raise typer.Exit(code=418)

    forge_version_info = None
    fabric_version_info = None
    if forge_version_promo_or_id and fabric_version_promo_or_id:
        err("无法同时安装 Forge 和 Fabric 加载器。")
        raise typer.Exit(code=500)

    info("正在查找 Minecraft 版本信息……")
    from mmccli.minecraft import load_mc_version_from_cache, save_launcher_profiles_json

    mc_version = load_mc_version_from_cache(mc_version_id, True)  # latest-release 和 latest-snapshot 在此方法内处理
    if not mc_version:
        err(f"未找到游戏版本 {mc_version_id}，请检查。")
        raise typer.Exit(code=404)

    if forge_version_promo_or_id:
        from mmccli.forge import load_forge_version_from_cache

        info("正在查找 Forge 版本信息……")
        forge_version_info = load_forge_version_from_cache(mc_version.id, forge_version_promo_or_id, True)
        if not forge_version_info:
            err(f"未找到支持 {mc_version.id} 的 Forge 版本 {forge_version_promo_or_id}，请检查。")
            raise typer.Exit(code=404)
        info(f"已确认 Forge 版本 {forge_version_info.name}")

    if fabric_version_promo_or_id:
        from mmccli.fabric import load_fabric_versions

        info("正在查找 Fabric 版本信息……")
        fabric_version_info = load_fabric_versions(mc_version.id, fabric_version_promo_or_id)
        if not fabric_version_info:
            err(f"未找到 Fabric 版本 {fabric_version_promo_or_id}，请检查。")
            raise typer.Exit(code=404)
        info(f"已确认 Fabric 版本 {fabric_version_info.loader.version}")

    if not name:
        name = mc_version.id
        if fabric_version_info:
            name += "-fabric-" + fabric_version_info.loader.version

    from mmccli.add import (
        analysis_forge_installer_version_json,
        download_assets,
        download_forge_installer_jar,
        download_libraries,
        download_mc_version_jar,
        load_assetsIndex_json,
        load_mc_version_json,
        save_assetIndex_json,
        save_mc_version_json,
    )

    version_json = load_mc_version_json(mc_version.url)
    vanilla_mc_version_id = version_json.id
    version_json.id = name  # 将自定义版本名称覆盖到 version.json
    info("已解析版本索引文件，开始下载库文件……")

    download_libraries(version_json.libraries, "minecraft")
    info("库文件下载完成，开始解析资源索引文件……")

    assetIndex_json = load_assetsIndex_json(version_json.assetIndex.url)
    info("已解析资源索引文件，开始下载资源文件……")

    download_assets(assetIndex_json)
    info("资源文件下载完成，开始下载游戏主文件……")

    download_mc_version_jar(
        vanilla_mc_version_id,
        version_json.downloads["client"],
        vanilla_mc_version_id if forge_version_info else name,
    )  # 由于 Forge 安装器需要基于合法的原版游戏进行安装，所以要保留合法的原版游戏。
    info("游戏主文件下载完成，保存资源索引……")

    save_assetIndex_json(version_json.assets, assetIndex_json)
    save_mc_version_json(version_json, vanilla_mc_version_id if forge_version_info else name)
    save_launcher_profiles_json(version_json)
    info(f"已添加 Minecraft Java {version_json.id}")

    if forge_version_info:
        forge_installer_path = download_forge_installer_jar(forge_version_info)
        info(f"已下载 Forge 安装器 {forge_version_info.name}，开始解析 Forge 版本信息……")

        forge_version_json, forge_install_profile_json = analysis_forge_installer_version_json(forge_installer_path)
        info("已解析 Forge 版本信息，开始下载 Forge 库文件……")

        download_libraries(forge_version_json.libraries + forge_install_profile_json.libraries, "forge")
        info("Forge 库文件下载完成，开始安装 Forge……")

        from mmccli.forge import install_forge_silently, rename_forge_version

        if install_forge_silently(str(forge_installer_path), str(useGlobalState.MINECRAFT)):
            rename_forge_version(vanilla_mc_version_id, forge_version_info.id, name)
            info(f"{forge_version_info.name} 已为 Minecraft {version_json.id} 安装成功。（共安装两个实例）")
        else:
            warn(f"{forge_version_info.name} 安装失败，但游戏本体应当安装成功。")

    if fabric_version_info:
        from mmccli.fabric import build_version_json_libraries_item, update_mc_version_json_with_fabric

        fabric_libraries = [
            build_version_json_libraries_item(
                name=library.name,
                base_url=library.url if library.url else "https://libraries.mojang.com/",
                size=library.size,
                sha1=library.sha1,
            )
            for library in fabric_version_info.launcherMeta.libraries.common
            + fabric_version_info.launcherMeta.libraries.client
        ]
        fabric_libraries.append(
            build_version_json_libraries_item(
                name=fabric_version_info.loader.maven,
                base_url="https://maven.fabricmc.net/",
            )
        )
        fabric_libraries.append(
            build_version_json_libraries_item(
                name=fabric_version_info.intermediary.maven,
                base_url="https://maven.fabricmc.net/",
            )
        )
        info("已解析 Fabric 版本信息，开始下载 Fabric 库文件……")

        download_libraries(fabric_libraries, "fabric")
        info("Fabric 库文件下载完成，更新版本 json 文件中……")

        save_mc_version_json(
            update_mc_version_json_with_fabric(
                version_json, fabric_libraries, fabric_version_info.launcherMeta.mainClass
            ),
            name,
        )
        info(f"Fabric loader {fabric_version_info.loader.version} 已为 Minecraft {version_json.id} 安装成功。")

    if useGlobalState.HARDLINK_DOWNGRADE_TO_FULL_COPY:
        warn("硬链接失败，已退化为全量复制文件。")


if __name__ == "__main__":
    app()
