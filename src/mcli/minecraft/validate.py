from pypdl.utils import FileValidator

from mcli.log import out, warn

from ._model import McGameAssetIndexJson_ObjectsItem
from .model import McGameVersionJson_LibrariesItem


def validate_libraries(libraries: list[McGameVersionJson_LibrariesItem], results: list[tuple[str, FileValidator]]):
    broken_libraries: list[McGameVersionJson_LibrariesItem] = []
    for item in libraries:
        for res in results:
            if res[0].endswith(item.downloads.artifact.path):
                if item.downloads.artifact.sha1 and res[1].get_hash("sha1") != item.downloads.artifact.sha1:
                    broken_libraries.append(item)

    if len(broken_libraries) > 0:
        warn(f"已下载的库文件中存在损坏 | 损坏 {len(broken_libraries)} / {len(results)}")
        for broken_item in broken_libraries:
            warn(f"* {broken_item.name}")
    else:
        out("已下载的库文件中没有损坏。")


def validate_assets(assets: list[McGameAssetIndexJson_ObjectsItem], results: list[tuple[str, FileValidator]]):
    broken_assets: list[McGameAssetIndexJson_ObjectsItem] = []
    for item in assets:
        for res in results:
            if res[0].endswith(item.hash):
                if res[1].get_hash("sha1") != item.hash:
                    broken_assets.append(item)

    if len(broken_assets) > 0:
        warn(f"已下载的资源文件中存在损坏 | 损坏 {len(broken_assets)} / {len(results)}")
        for broken_item in broken_assets:
            warn(f"* {broken_item.hash}")
    else:
        out("已下载的资源文件中没有损坏。")
