# mmccli.forge.promos
import json
import os
from typing import Literal

import requests

from mmccli.cache import CACHE_ROOT_DIR
from mmccli.log import RequestStatusError, out, warn

from .model import (
    ForgeInstallerVersionInfo,
    ForgePromosListJson,
    ForgePromosListJson_Item,
    ForgeVersionItem,
    ForgeVersionListJson,
)

CACHE_DIR = CACHE_ROOT_DIR / "manifest"
CACHE_DIR.mkdir(exist_ok=True)


def load_forge_promos(save: bool = False) -> ForgePromosListJson:
    url = os.environ.get("MCLI_FORGE_PROMOS_URL", "https://bmclapi2.bangbang93.com/forge/promos")
    out(url)
    response = requests.get(url)
    data = response.json()
    if not response.ok:
        raise RequestStatusError(f"获取 Forge promos 时失败 | {url=}")
    promos_data = ForgePromosListJson.model_validate(data)

    if save:
        from datetime import date

        now_date = date.today()
        out(f"缓存为 {now_date} froge_promos.json。")
        with open(
            file=CACHE_DIR / f"forge_promos_{now_date.year}_{now_date.month}_{now_date.day}.json",
            mode="w",
            encoding="UTF-8",
        ) as f:
            f.write(json.dumps(data, indent=4))

    return promos_data


def load_forge_promos_from_cache(load_when_miss: bool = False) -> ForgePromosListJson | Literal[False]:
    from datetime import date

    now_date = date.today()
    file = CACHE_DIR / f"forge_promos_{now_date.year}_{now_date.month}_{now_date.day}.json"
    failed = True
    if file.is_file():
        try:
            with open(file=file, mode="r", encoding="UTF-8") as f:
                promos_data = ForgePromosListJson.model_validate_json(f.read())
                failed = False
                out("成功从缓存读取 forge_promos.json")
                return promos_data
        except Exception as e:
            out("从缓存读取 froge_promos.json 失败：")
            out(e)

    if failed and load_when_miss:
        return load_forge_promos(True)

    return False


def load_forge_version_from_cache(
    mc_version_id: str, version_id: str, load_when_miss: bool = False
) -> ForgeInstallerVersionInfo | Literal[False]:
    if version_id == "recommended" or version_id == "latest":
        promos_data = load_forge_promos_from_cache(load_when_miss=load_when_miss)
        if not promos_data:
            warn("加载 forge_promos.json 失败。")
            return False

        target = mc_version_id + "-" + version_id
        for item in promos_data:
            item: ForgePromosListJson_Item
            if target == item.name:
                item_hash = None
                for file in item.build.files:
                    if file.format == "jar" and file.category == "installer":
                        item_hash = file.hash
                if not item_hash:
                    raise RuntimeError(f"Unexpected exception: No installer hash in {item=}")
                return ForgeInstallerVersionInfo(
                    id=item.build.version,
                    build=item.build.build,
                    hash=item_hash,
                    name=f"forge-installer-{mc_version_id}-{item.build.version}.jar",
                )

        if version_id == "recommended":
            out(f"forge promos 查找策略从 {mc_version_id}-recommended 回退到 {mc_version_id}-latest")
            target = mc_version_id + "-latest"
            for item in promos_data:
                item: ForgePromosListJson_Item
                if target == item.name:
                    item_hash = None
                    for file in item.build.files:
                        if file.format == "jar" and file.category == "installer":
                            item_hash = file.hash
                    if not item_hash:
                        raise RuntimeError(f"Unexpected exception: No installer hash in {item=}")
                    return ForgeInstallerVersionInfo(
                        id=item.build.version,
                        build=item.build.build,
                        hash=item_hash,
                        name=f"forge-installer-{mc_version_id}-{item.build.version}.jar",
                    )

        out(f"查找 forge promos 版本 {mc_version_id}-{version_id} 失败。")
        return False

    else:
        url = f"https://bmclapi2.bangbang93.com/forge/minecraft/{mc_version_id}"
        response = requests.get(url)
        out(url)
        data = response.json()
        if not response.ok:
            warn(f"加载 {mc_version_id} 游戏版本支持的 Forge 列表失败。")
            out(data)
            return False

        forge_list = ForgeVersionListJson.model_validate(data)
        for item in forge_list:
            item: ForgeVersionItem
            if item.version == version_id:
                item_hash = None
                for file in item.files:
                    if file.format == "jar" and file.category == "installer":
                        item_hash = file.hash
                if not item_hash:
                    raise RuntimeError(f"Unexpected exception: No installer hash in {item=}")
                return ForgeInstallerVersionInfo(
                    id=item.version,
                    build=item.build,
                    hash=item_hash,
                    name=f"forge-installer-{mc_version_id}-{item.version}.jar",
                )

        out(f"查找 Forge 版本 {mc_version_id}-{version_id} 失败。")
        return False
