# mmccli.minecraft.add
import os
import ssl
import time
from pathlib import Path
from typing import Literal

import certifi
import requests
from rich.live import Live
from rich.text import Text

from mmccli.cache import (
    get_assets_cache_file_path,
    get_forge_installer_cache_file_path,
    get_library_cache_file_path,
    get_version_jar_cache_file_path,
)
from mmccli.download import DownloadTask, start_download_task, start_download_tasks
from mmccli.forge import ForgeInstallerVersionInfo
from mmccli.forge.model import ForgeInstallerInstallProfileJson, ForgeInstallerVersionJson
from mmccli.log import RequestStatusError, console, out, useGlobalState
from mmccli.minecraft import (
    McGameAssetIndexJson,
    McGameVersionJson,
    McGameVersionJson_FileModel,
    McGameVersionJson_LibrariesItem,
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
    libraries_from: Literal["minecraft", "forge", "fabric"],
):
    if not useGlobalState.MINECRAFT:
        raise RuntimeError(f"Unexpected value of {useGlobalState.MINECRAFT=}")
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
        raise RuntimeError(f"Unexpected value of {libraries_from=}")

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
    tasks: list[DownloadTask] = []
    total_size = 0
    for item in download_list:
        item: McGameVersionJson_LibrariesItem  # type: ignore[no-redef]
        if item.downloads.artifact.url == "":  # 为什么会存在 library 的 url 为空呢？
            continue  # 原来这个玩意是不需要手动下载的呀！
        file_path = useGlobalState.MINECRAFT / "libraries" / item.downloads.artifact.path  # 游戏目录中的库文件路径
        file_path.parent.mkdir(exist_ok=True, parents=True)
        cache_file_path = get_library_cache_file_path(item.downloads.artifact.path)  # 缓存中的库文件路径
        cache_file_path.parent.mkdir(exist_ok=True, parents=True)
        if item.downloads.artifact.size:
            total_size += item.downloads.artifact.size
        url = (
            item.downloads.artifact.url.replace(template_url_prefix, base_url)
            if base_url
            else item.downloads.artifact.url
        )
        tasks.append(
            DownloadTask(
                url=url,
                url2=item.downloads.artifact.url if base_url else None,
                file_path=file_path,
                cache_file_path=cache_file_path,
                size=item.downloads.artifact.size,
                sha1=item.downloads.artifact.sha1,
            )
        )

    _multi_download_with_progress(tasks, total_size)
    out("库文件已下载完成。")


def download_assets(assetIndex_data: McGameAssetIndexJson):
    if not useGlobalState.MINECRAFT:
        raise RuntimeError(f"Unexpected value of {useGlobalState.MINECRAFT=}")
    # 拼装任务列表，批量下载
    tasks: list[DownloadTask] = []
    total_size = 0
    base_url = os.environ.get("MCLI_MC_GAME_DOWNLOAD_ASSETS_URL", None)
    for item in assetIndex_data.objects.values():
        file_path = useGlobalState.MINECRAFT / "assets" / "objects" / item.hash[:2] / item.hash
        cache_file_path = get_assets_cache_file_path(f"objects/{item.hash[:2]}/{item.hash}")
        total_size += item.size
        path = item.hash[:2] + "/" + item.hash
        url = (base_url if base_url else "https://resources.download.minecraft.net/") + path
        tasks.append(
            DownloadTask(
                url=url,
                url2=("https://resources.download.minecraft.net/" + path) if base_url else None,
                file_path=file_path,
                cache_file_path=cache_file_path,
                size=item.size,
                sha1=item.hash,
            )
        )

    _multi_download_with_progress(tasks, total_size, 64)
    out("资源文件已下载完成。")


def download_mc_version_jar(version_id: str, clientItem: McGameVersionJson_FileModel, name: str):
    if not useGlobalState.MINECRAFT:
        raise RuntimeError(f"Unexpected value of {useGlobalState.MINECRAFT=}")
    file_path = useGlobalState.MINECRAFT / "versions" / name / (name + ".jar")
    cache_file_path = get_version_jar_cache_file_path("client/" + version_id + ".jar")
    base_url = os.environ.get("MCLI_MC_GAME_DOWNLOAD_VERSIONS_URL", None)
    _single_download_with_progress(
        DownloadTask(
            url=clientItem.url.replace("https://piston-data.mojang.com/", base_url) if base_url else clientItem.url,
            url2=clientItem.url if base_url else None,
            file_path=file_path,
            cache_file_path=cache_file_path,
            size=clientItem.size,
            sha1=clientItem.sha1,
        )
    )
    out("版本 jar 游戏主文件下载完成。")


def download_forge_installer_jar(info: ForgeInstallerVersionInfo):
    # Forge 安装器仅存放在缓存中
    file_path = get_forge_installer_cache_file_path(info.name)
    file_path.parent.mkdir(exist_ok=True, parents=True)
    _single_download_with_progress(
        DownloadTask(
            url=f"https://bmclapi2.bangbang93.com/forge/download/{info.build}",
            file_path=file_path,
        )
    )
    return file_path


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


def _multi_download_with_progress(tasks: list[DownloadTask], total_size: int, sem_max: int = 32):
    from math import floor

    total_task = len(tasks)
    useGlobalState.DOWNLOAD_TASK_DOING = total_task
    thread = start_download_tasks(tasks, sem_max)

    def update_live(completed_size: int, completed_task: int):
        percent = min(40, floor(completed_task / total_task * 40))
        return (
            Text(text="[多任务下载中]", style="cyan on #495057")
            + Text(text="\t<", style="default on default")
            + Text(text="=" * percent, style="green on default")
            + Text(text="=" * (40 - percent), style="default on default")
            + Text(text=">\t[", style="default on default")
            + Text(text=f"{completed_task}", style="green on default")
            + Text(text="/", style="default on default")
            + Text(text=f"{total_task}", style="#f7b1b0 on default")
            + Text(text="]\t[", style="default on default")
            + Text(text=f"{completed_size / 1_000}KB", style="green on default")
            + Text(text="/", style="default on default")
            + Text(text=f"{total_size / 1_000}KB", style="#f7b1b0 on default")
            + Text(text="]", style="default on default")
        )

    with Live(update_live(0, 0), console=console, refresh_per_second=2, transient=True) as live:
        while useGlobalState.DOWNLOAD_CONTINUE:
            live.update(
                update_live(
                    completed_size=useGlobalState.DOWNLOAD_SIZE_COMPLETE,
                    completed_task=useGlobalState.DOWNLOAD_TASK_COMPLETE,
                )
            )
            time.sleep(0.5)
    thread.join()


def _single_download_with_progress(task: DownloadTask):
    thread = start_download_task(task)

    def update_live(completed_size: int):
        display = (
            Text(text="[单任务下载中]", style="cyan on #495057")
            + Text(text="\t「", style="default on default")
            + Text(text="Fly higher my friend.", style="green on default")
            + Text(text="」", style="default on default")
        )
        if task.size:
            display += (
                Text(text="\t[", style="default on default")
                + Text(text=f"{completed_size / 1_000}KB", style="green on default")
                + Text(text="/", style="default on default")
                + Text(f"{task.size / 1_000}KB", style="#f7b1b0 on default")
                + Text(text="]", style="default on default")
            )
        else:
            display += (
                Text(text="\t[", style="default on default")
                + Text(text=f"{completed_size / 1_000}KB", style="green on default")
                + Text(text="]", style="default on default")
            )
        return display

    with Live(update_live(0), console=console, refresh_per_second=2, transient=True) as live:
        while useGlobalState.DOWNLOAD_CONTINUE:
            live.update(update_live(completed_size=useGlobalState.DOWNLOAD_SIZE_COMPLETE))
            time.sleep(0.5)
    thread.join()
