import os

import requests

from mmccli.cache import CACHE_ROOT_DIR
from mmccli.log import RequestStatusError, out

from .model import FabricMetaVersions, FabricMetaVersions_LoaderItem

CACHE_DIR = CACHE_ROOT_DIR / "manifest"
CACHE_DIR.mkdir(exist_ok=True)


def load_fabric_versions(mc_version_id: str, version_id: str):
    url = (
        os.environ.get("MCLI_FABRIC_META_VERSIONS_V2_URL", "https://meta.fabricmc.net/v2/versions/loader/")
        + mc_version_id
    )
    out(url)
    response = requests.get(url)
    data = response.json()
    if not response.ok:
        raise RequestStatusError(f"获取 {mc_version_id=} 对应的 Fabric 版本清单失败 | {url=}")
    fabric_versions = FabricMetaVersions.model_validate(data)

    if version_id == "latest":
        return fabric_versions[0]

    for version in fabric_versions:
        version: FabricMetaVersions_LoaderItem
        if version.loader.version == version_id:
            return version

    out(f"查找 Fabric 版本 {version_id} 失败。")
    return False
