# mmccli.app
from dotenv import load_dotenv

load_dotenv()

# 务必首先导入环境变量~

from typing import Annotated

import typer

from mmccli.log import err, info, useGlobalState, warn
from mmccli.minecraft import app_minecraft
from mmccli.path_dector import detect_minecraft_install_folder

app = typer.Typer(help="Minecraft Java Cli", name="MCLI")
app.add_typer(app_minecraft)


@app.command()
def login():
    """
    登录微软账号，验证您的 Minecraft Java 版游戏所有权。

    由于未获得 Mojang 批准所以 TvT
    """
    err("正版登录尚不可用，因为 Mojang 没有批准 MCLI 访问其游戏服务 API。")
    raise typer.Exit(code=100)


@app.command()
def add(
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
