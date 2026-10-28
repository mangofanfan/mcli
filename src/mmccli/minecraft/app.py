# mmccli.minecraft.app

from typing import Annotated, Literal

import typer
from rich.table import Table

from mmccli.log import err, info, raw

from .manifests import load_mc_manifest_v2, load_mc_manifest_v2_from_cache

app = typer.Typer(help="管理 Minecraft 版本实例的子命令。", name="minecraft")


@app.command()
def manifest():
    """
    获取、更新 manifest.json 文件，以更新版本列表。

    通常情况下，每天 MCLI 都会自动更新一次。此命令会立刻重新更新 manifest。

    通过环境变量 MCLI_MC_GAME_VERSION_MANIFEST_V2_JSON 设置 manifest URL，仅支持 v2 格式。
    """
    info("获取 manifest.json 中……")
    load_mc_manifest_v2(save=True)
    info("已获取 manifest.json 并刷新缓存。")


@app.command(name="list")
def list_version(
    version_type: Annotated[
        Literal["release", "snapshot", "all"], typer.Option("--type", "-t", help="列出的版本类型")
    ] = "all",
    limit: Annotated[int, typer.Option("--limit", "-l", help="列出版本的数量，0 表示全部列出")] = 20,
):
    """
    列出所有可供下载的 Minecraft 游戏版本。

    会尝试复用当日的 manifest.json 缓存，缓存失效时尝试从 URL 获取，此时行为与 manifest 命令一致。
    """
    info("获取并解析 manifest.json ……")
    from datetime import datetime

    manifest_data = load_mc_manifest_v2_from_cache(True)
    if not manifest_data:
        err("获取 manifest.json 缓存时失败，原因未知。")

    count = 0
    table = Table("id", "type", "time", "releaseTime")
    for version in manifest_data.versions:
        if 0 < limit <= count:
            break
        if (
            (version_type == "all" or version_type == version.type)
            and version.type != "old_alpha"
            and version.type != "old_beta"
        ):
            table.add_row(
                version.id,
                version.type,
                str(datetime.fromisoformat(version.time)),
                str(datetime.fromisoformat(version.releaseTime)),
            )
            count += 1
    raw(table)
    info(f"已列出 {count} 个 Minecraft 版本。")
