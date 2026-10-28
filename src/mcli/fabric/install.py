# mcli.fabric.install
import os

from mcli.fabric.model import FabricMetaVersions_LoaderItem_LauncherMeta_MainClass
from mcli.minecraft import (
    McGameVersionJson,
    McGameVersionJson_LibrariesItem,
    McGameVersionJson_LibrariesItemDownloads,
    McGameVersionJson_LibrariesItemDownloadsArtifact,
)


def build_version_json_libraries_item(name: str, base_url: str, size: int | None = None, sha1: str | None = None):
    """
    产出依赖库结构中，path 是根据 name 拼接得到的，url 是根据 path 拼接完整的，sha1 是可能没有的。
    :return:
    """

    parts: list[str] = name.split(":")  # 长度为 3，形如 ["net.fabricmc", "fabric-loader", "0.16.14"]

    path = "/".join(parts[0].split(".")) + "/" + parts[1] + "/" + parts[2] + "/" + parts[1] + "-" + parts[2] + ".jar"

    return McGameVersionJson_LibrariesItem(
        name=name,
        downloads=McGameVersionJson_LibrariesItemDownloads(
            artifact=McGameVersionJson_LibrariesItemDownloadsArtifact(
                path=path,
                url=os.environ.get("MCLI_FABRIC_DOWNLOAD_LIBRARIES_URL", base_url) + path,
                size=size,
                sha1=sha1,
            )
        ),
    )


def update_mc_version_json_with_fabric(
    version_json: McGameVersionJson,
    fabric_libraries: list[McGameVersionJson_LibrariesItem],
    mainClass: FabricMetaVersions_LoaderItem_LauncherMeta_MainClass | str,
):
    version_json.libraries += fabric_libraries
    version_json.mainClass = mainClass if isinstance(mainClass, str) else mainClass.client
    return version_json
