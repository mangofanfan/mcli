# mmccli.minecraft.add
import json
import os
import ssl
import time
from pathlib import Path
from typing import Literal

import certifi
import requests
from pypdl import Pypdl
from pypdl.utils import EFuture, FileValidator
from rich.progress import Progress

from mmccli.cache import (
    get_assets_cache_file_path,
    get_forge_installer_cache_file_path,
    get_library_cache_file_path,
    get_version_jar_cache_file_path,
    link_or_move,
)
from mmccli.forge import ForgeInstallerVersionInfo
from mmccli.forge.model import ForgeInstallerInstallProfileJson, ForgeInstallerVersionJson
from mmccli.log import RequestStatusError, console, out, warn
from mmccli.minecraft import (
    McGameAssetIndexJson,
    McGameVersionJson,
    McGameVersionJson_FileModel,
    McGameVersionJson_LibrariesItem,
    McLauncherLaunchProfilesJson,
    McLauncherLaunchProfilesJson_ProfilesItem,
    validate_assets,
    validate_libraries,
)

ssl_context = ssl.create_default_context(cafile=certifi.where())

COPY_DICT = dict[str | Path, str | Path]


def load_mc_version_json(version_json_url: str) -> McGameVersionJson:
    response = requests.get(version_json_url)
    out(version_json_url)
    data = response.json()
    if not response.ok:
        raise RequestStatusError(f"获取游戏版本 version.json 时请求失败 | {version_json_url=}")
    return McGameVersionJson.model_validate(data)


def load_assetsIndex_json(assetIndex_json_url: str) -> McGameAssetIndexJson:
    response = requests.get(assetIndex_json_url)
    out(assetIndex_json_url)
    data = response.json()
    if not response.ok:
        raise RequestStatusError(f"获取游戏资源索引 assetIndex.json 时请求失败 | {assetIndex_json_url=}")
    return McGameAssetIndexJson.model_validate(data)


def download_libraries(
    libraries: list[McGameVersionJson_LibrariesItem],
    dl: Pypdl,
    libraries_from: Literal["minecraft", "forge", "fabric"],
):
    if libraries_from == "minecraft":
        base_url = os.environ.get("MCLI_MC_GAME_DOWNLOAD_LIBRARIES_URL", None)
        template_url_prefix = "https://libraries.minecraft.net/"
    elif libraries_from == "forge":
        base_url = os.environ.get("MCLI_FORGE_DOWNLOAD_LIBRARIES_URL", None)
        template_url_prefix = "https://maven.minecraftforge.net/"
    elif libraries_from == "fabric":
        base_url = os.environ.get("MCLI_FABRIC_DOWNLOAD_LIBRARIES_URL", None)
        template_url_prefix = "https://maven.fabricmc.net/"
    else:
        raise RuntimeError(f"Unexpected value {libraries_from=}")

    # 并非所有库文件都要下载，此处存放需要下载的库文件
    download_list: list[McGameVersionJson_LibrariesItem] = []

    for item in libraries:
        if item.rules is None:  # 没有 rules 的 library
            download_list.append(item)
            continue

        for rule in item.rules:
            if rule.action == "allow" and rule.os and rule.os.name == "windows":
                download_list.append(item)

    # 拼装任务列表，批量下载
    tasks = []
    copy_dict: COPY_DICT = {}
    total_size = 0
    for item in download_list:
        item: McGameVersionJson_LibrariesItem  # type: ignore[no-redef]
        if item.downloads.artifact.url == "":  # 为什么会存在 library 的 url 为空呢？
            continue  # 原来这个玩意是不需要手动下载的呀！
        file_path = Path.cwd() / ".minecraft" / "libraries" / item.downloads.artifact.path  # 游戏目录中的库文件路径
        file_path.parent.mkdir(exist_ok=True, parents=True)
        cache_file_path = get_library_cache_file_path(item.downloads.artifact.path)  # 缓存中的库文件路径
        cache_file_path.parent.mkdir(exist_ok=True, parents=True)
        copy_dict[file_path] = cache_file_path  # 建立关联
        if cache_file_path.exists():
            continue  # 信任缓存，跳过缓存命中
        if item.downloads.artifact.size:
            total_size += item.downloads.artifact.size
        url = (
            item.downloads.artifact.url.replace(template_url_prefix, base_url)
            if base_url
            else item.downloads.artifact.url
        )
        out(url)
        tasks.append(
            {
                "url": url,
                "file_path": str(cache_file_path),
                "retries": 2,
                "segments": 8 if item.downloads.artifact.size and item.downloads.artifact.size >= 2_000_000 else 2,
                "mirrors": item.downloads.artifact.url if base_url else None,
            }
        )
    out(f"待下载库文件数量 | {len(tasks)=}")

    if len(tasks) > 0:
        results = _multi_download_with_progress(tasks, total_size, dl)
        validate_libraries(download_list, results)
    out("链接或复制文件……")

    for file_path, cache_file_path in copy_dict.items():  # type: ignore[assignment]
        link_or_move(cache_file_path, file_path)
    out("库文件已下载完成。")


def download_assets(assetIndex_data: McGameAssetIndexJson, dl: Pypdl):
    # 拼装任务列表，批量下载
    tasks = []
    copy_dict: COPY_DICT = {}
    total_size = 0
    base_url = os.environ.get("MCLI_MC_GAME_DOWNLOAD_ASSETS_URL", None)
    for item in assetIndex_data.objects.values():
        file_path = Path.cwd() / ".minecraft" / "assets" / "objects" / item.hash[:2] / item.hash
        file_path.parent.mkdir(exist_ok=True, parents=True)
        cache_file_path = get_assets_cache_file_path(f"objects/{item.hash[:2]}/{item.hash}")
        cache_file_path.parent.mkdir(exist_ok=True, parents=True)
        copy_dict[file_path] = cache_file_path
        if cache_file_path.exists():
            continue  # 信任缓存，跳过缓存命中
        total_size += item.size
        path = item.hash[:2] + "/" + item.hash
        url = (base_url if base_url else "https://resources.download.minecraft.net/") + path
        out(url)
        tasks.append(
            {
                "url": url,
                "file_path": str(cache_file_path),
                "retries": 2,
                "segments": 4 if item.size >= 1_000_000 else 1,
                "mirrors": ("https://resources.download.minecraft.net/" + path) if base_url else None,
            }
        )
    out(f"待下载资源文件数量 | {len(tasks)=}")

    if len(tasks) > 0:
        results = _multi_download_with_progress(tasks, total_size, dl)
        validate_assets(list(assetIndex_data.objects.values()), results)
    out("链接或复制文件……")

    for file_path, cache_file_path in copy_dict.items():  # type: ignore[assignment]
        link_or_move(cache_file_path, file_path)
    out("资源文件已下载完成。")


def download_mc_version_jar(version_id: str, clientItem: McGameVersionJson_FileModel, dl: Pypdl, name: str):
    file_path = Path.cwd() / ".minecraft" / "versions" / name / (name + ".jar")
    file_path.parent.mkdir(exist_ok=True, parents=True)
    cache_file_path = get_version_jar_cache_file_path("client/" + version_id + ".jar")
    cache_file_path.parent.mkdir(exist_ok=True, parents=True)
    base_url = os.environ.get("MCLI_MC_GAME_DOWNLOAD_VERSIONS_URL", None)
    if not cache_file_path.exists():  # 信任缓存
        result = _single_download_with_progress(
            url=clientItem.url.replace("https://piston-data.mojang.com/", base_url) if base_url else clientItem.url,
            mirrors=clientItem.url if base_url else None,
            file_path=str(cache_file_path),
            size=clientItem.size,
            dl=dl,
        )
        if result[0][1].get_hash("sha1") != clientItem.sha1:
            warn("下载的版本游戏主文件 version.jar 存在损坏。")
    out("链接或复制文件……")

    link_or_move(cache_file_path, file_path)
    out("版本 jar 游戏主文件下载完成。")


def download_forge_installer_jar(info: ForgeInstallerVersionInfo, dl: Pypdl):
    cache_file_path = get_forge_installer_cache_file_path(info.name)
    cache_file_path.parent.mkdir(exist_ok=True, parents=True)
    if not cache_file_path.exists():  # 信任缓存
        result = _single_download_with_progress(
            url=f"https://bmclapi2.bangbang93.com/forge/download/{info.build}",
            file_path=str(cache_file_path),
            dl=dl,
        )
        if result[0][1].get_hash("sha1") != info.hash:
            warn("下载的 Forge 安装器文件存在损坏。")

    return cache_file_path


def analysis_forge_installer_version_json(file_path: str):
    from tempfile import TemporaryDirectory
    from zipfile import ZipFile

    with TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)
        with ZipFile(file=file_path, mode="r") as z:
            z.extractall(tmp_path / "forge-installer-extractall")

        with open(file=tmp_path / "forge-installer-extractall" / "version.json") as f:
            version_json = ForgeInstallerVersionJson.model_validate_json(f.read())

        with open(file=tmp_path / "forge-installer-extractall" / "install_profile.json") as f:
            install_profile_json = ForgeInstallerInstallProfileJson.model_validate_json(f.read())

    out("已在临时目录解压并解析 Forge 安装器内的 version.json 和 install_profile.json")
    return version_json, install_profile_json


def save_mc_version_json(version_json: McGameVersionJson, name: str):
    file_path = Path.cwd() / ".minecraft" / "versions" / name / (name + ".json")
    file_path.parent.mkdir(exist_ok=True, parents=True)
    with open(file=file_path, mode="w", encoding="UTF-8") as f:
        f.write(version_json.model_dump_json(exclude_unset=True, indent=4))
    out("已保存版本 json 文件。")


def save_assetIndex_json(assetIndex_id: str, assetIndex_json: McGameAssetIndexJson):
    file_path = Path.cwd() / ".minecraft" / "assets" / "indexes" / (assetIndex_id + ".json")
    file_path.parent.mkdir(exist_ok=True, parents=True)
    with open(file=file_path, mode="w", encoding="UTF-8") as f:
        f.write(assetIndex_json.model_dump_json(exclude_unset=True, indent=4))
    out("已保存资源文件索引 json 文件。")


def save_launcher_profiles_json(mc_version_json: McGameVersionJson):
    from datetime import datetime
    from uuid import uuid4

    key = uuid4().hex
    now = datetime.now()

    # 已有启动器配置文件就写入，否则新建
    file_path = Path.cwd() / ".minecraft" / "launcher_profiles.json"
    file_path.parent.mkdir(exist_ok=True, parents=True)
    profile = McLauncherLaunchProfilesJson_ProfilesItem(
        created=now.isoformat(),
        icon="Grass",
        javaArgs="-Xms2G -Xmx4G -XX:+UseCompactObjectHeaders -XX:+AlwaysPreTouch -XX:+UseStringDeduplication -XX:+UseZGC",
        lastUsed="1970-01-01T00:00:00.000Z",
        lastVersionId=mc_version_json.id,
        name=mc_version_json.id,
        type="custom",
    )
    if file_path.exists():
        with open(file=file_path, mode="r") as f:
            launcher_profiles = McLauncherLaunchProfilesJson.model_validate_json(f.read())
            launcher_profiles.profiles["key"] = profile
    else:
        launcher_profiles = McLauncherLaunchProfilesJson(
            profiles={key: profile},
            settings={},
            version=6,
        )
    with open(file=file_path, mode="w", encoding="UTF-8") as f:
        f.write(launcher_profiles.model_dump_json(indent=4))
    out("已更新或新建启动器配置 json 文件。")


def _multi_download_with_progress(tasks: list[dict], total_size: int, dl: Pypdl) -> list[tuple[str, FileValidator]]:
    future: EFuture = dl.start(
        tasks=tasks,
        block=False,
        hash_algorithms="sha1",
        display=False,
        proxy=os.environ.get("HTTP_PROXY", None),
        overwrite=False,
        ssl=ssl_context,
    )

    if len(tasks) > 0:
        with Progress(console=console, transient=True) as progress:
            task_files = progress.add_task("[cyan]下载总文件", total=dl.total_task)
            task_size = progress.add_task("[green]下载总空间", total=total_size)
            while not dl.completed:
                progress.update(task_files, completed=dl.completed_task)
                progress.update(task_size, completed=dl.current_size)
                time.sleep(0.5)

    return future.result()  # type: ignore[no-any-return]


def _single_download_with_progress(
    url: str,
    file_path: str,
    dl: Pypdl,
    mirrors: str | list[str] | None = None,
    size: int | None = None,
) -> list[tuple[str, FileValidator]]:
    future: EFuture = dl.start(
        url=url,
        file_path=file_path,
        mirrors=mirrors,
        segments=8,
        retries=2,
        block=False,
        overwrite=False,
        hash_algorithms="sha1",
        display=False,
        proxy=os.environ.get("HTTP_PROXY", None),
        ssl=ssl_context,
    )

    with Progress(console=console, transient=True) as progress:
        task_size = progress.add_task("[green]下载空间", total=size)
        while not dl.completed:
            progress.update(task_size, completed=dl.current_size)
            time.sleep(0.5)

    return future.result()  # type: ignore[no-any-return]
