# mmccli.minecraft.manifests
import json
import os

import requests

from mmccli.cache import CACHE_ROOT_DIR
from mmccli.log import out, warn
from mmccli.log.error import RequestStatusError
from .model import McGameVersionManifestV2

CACHE_DIR = CACHE_ROOT_DIR / "manifest"
CACHE_DIR.mkdir(exist_ok=True)


def load_mc_manifest_v2(save: bool = False):
    url = os.environ.get("MCLI_MC_GAME_VERSION_MANIFEST_V2_JSON",
                         "https://launchermeta.mojang.com/mc/game/version_manifest_v2.json")

    response = requests.get(url)
    data = response.json()
    if not response.ok:
        raise RequestStatusError(f"获取 manifest_v2.json 文件失败 | {url=}")
    manifest_data = McGameVersionManifestV2.model_validate(data)

    if save:
        from datetime import date

        now_date = date.today()
        out(f"缓存为 {now_date} manifest.json。")
        with open(file=CACHE_DIR / f"manifest_{now_date.year}_{now_date.month}_{now_date.day}.json", mode="w",
                  encoding="UTF-8") as f:
            f.write(json.dumps(data, indent=4))

    return manifest_data


def load_mc_manifest_v2_from_cache(load_when_miss: bool = False):
    from datetime import date

    now_date = date.today()
    file = CACHE_DIR / f"manifest_{now_date.year}_{now_date.month}_{now_date.day}.json"
    failed = True
    if file.is_file():
        try:
            with open(file=file, mode="r", encoding="UTF-8") as f:
                manifest_data = McGameVersionManifestV2.model_validate_json(f.read())
                failed = False
                out("成功从缓存读取 manifest.json")
                return manifest_data
        except Exception as e:
            out("从缓存读取 manifest.json 失败：")
            out(e)

    if failed and load_when_miss:
        return load_mc_manifest_v2(True)

    return False


def load_mc_version_from_cache(version_id: str, load_when_miss: bool = False):
    manifest_data = load_mc_manifest_v2_from_cache(load_when_miss=load_when_miss)
    if not manifest_data:
        warn("加载 manifest.json 失败。")
        return False

    if version_id == "latest-release":
        out("查找到的最近正式版条目：")
        version = manifest_data.latest["release"]
        out(version)
        return version
    elif version_id == 'latest-snapshot':
        out("查找到的最近快照版条目：")
        version = manifest_data.latest["snapshot"]
        out(version)
        return version

    for version in manifest_data.versions:
        if version_id == version.id:
            out("查找到的 version 条目：")
            out(version)
            return version

    out(f"未查找到 {version_id} 对应的游戏版本条目。")
    return False
