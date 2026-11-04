# mmccli.cache.app

import shutil
from enum import Enum
from pathlib import Path
from typing import Annotated

import typer
from rich import box
from rich.table import Table

from mmccli.log import console_stdout, info, out

from ._lib import CACHE_ROOT_DIR

app = typer.Typer(help="管理全局缓存。", name="cache")


class CACHE_TYPE(str, Enum):
    assets = "assets"
    libraries = "libraries"
    versions = "versions"
    forge_installer = "forge-installer"


@app.command(name="size")
def mmccli_cache_size():
    """计算全局缓存大小"""
    table = Table(show_header=False, box=box.SIMPLE)
    table.add_column(style="yellow")
    table.add_column(style="white")
    table.add_column(justify="right", style="cyan")
    table.add_column(justify="right", style="green")

    def _stat_folder(path: Path) -> tuple[int, int]:  # 文件数量、总占用空间（B）
        number, size = 0, 0
        for item in path.rglob("*"):
            if item.is_file() and not item.is_symlink():
                _s = item.stat().st_size
                number += 1
                size += _s
                out(f"+ {item!s} : size={_s}")
            elif item.is_dir():
                _n, _s = _stat_folder(item)
                number += _n
                size += _s
            else:
                out(f"~ {item!s} : not directory or un-symlink file.")
        return number, size

    def _stat(path: Path) -> tuple[int, int]:  # 文件数量、总占用空间（B）
        return _stat_folder(path)

    def _data(folder: str):
        path = CACHE_ROOT_DIR / folder
        number, size = _stat(path)
        table.add_row(folder, str(path), "{number} files".format(number=number), "{size} KB".format(size=size / 1_000))

    _data("assets")
    _data("libraries")
    _data("versions")
    _data("forge-installer")

    console_stdout.print(table)


@app.command(name="clean")
def mmccli_cache_clean(
    types: Annotated[
        list[CACHE_TYPE] | None,
        typer.Argument(
            help="要清理的缓存类别，留空将全部清理",
        ),
    ] = None,
):
    """清理缓存，释放空间。"""

    def _clean(folder: CACHE_TYPE):
        path = CACHE_ROOT_DIR / folder.value
        if path.is_dir():
            shutil.rmtree(path)
            out("已清理缓存 {folder} : {path}".format(folder=folder.value, path=str(path)))
        else:
            out("缓存目录不存在 {folder} : {path}".format(folder=folder.value, path=str(path)))

    if not types or len(types) == 0:
        _clean(CACHE_TYPE.assets)
        _clean(CACHE_TYPE.libraries)
        _clean(CACHE_TYPE.versions)
        _clean(CACHE_TYPE.forge_installer)
    else:
        for item in types:
            _clean(item)

    info("已清理缓存。")
