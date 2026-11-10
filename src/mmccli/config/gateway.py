# mmccli.config.gateway

import os
import platform
from pathlib import Path
from typing import Any

import tomlkit

from mmccli.log import warn

from .config_item import McliConfig_LogLevel
from .state import McliConfig

match platform.system():
    case "Windows":
        ENV_HOME_NAME = "USERPROFILE"
    case _:
        ENV_HOME_NAME = "HOME"
CONFIG_ROOT_DIR = Path(os.environ.get(ENV_HOME_NAME, "")) / ".config" / "mmccli"


def save_config_to_file(key: str, value: Any):
    path = CONFIG_ROOT_DIR / "mmccli.toml"
    key = key.lower()

    if path.exists():
        with open(file=path, mode="r", encoding="UTF-8") as f:
            doc = tomlkit.parse(f.read())
    else:
        doc = tomlkit.document()
        doc.add(tomlkit.comment("mmccli/mmccli.toml"))
        doc.add(tomlkit.comment("see https://mango.js.cn/docs/mcli/concept/config"))
        doc.add(tomlkit.comment("If you cannot find where this file: ~/.config/mmccli/mmccli.toml"))
        doc.add(tomlkit.nl())

    if key.startswith("minecraft_"):
        title = "minecraft"
        name = key.removeprefix("minecraft_").replace("_", "-")
    elif key.startswith("forge_"):
        title = "forge"
        name = key.removeprefix("forge_").replace("_", "-")
    elif key.startswith("fabric_"):
        title = "fabric"
        name = key.removeprefix("fabric_").replace("_", "-")
    else:
        title = "mcli"
        name = key.replace("_", "-")

    if title in doc:
        table: tomlkit.api.Table = doc[title]
    else:
        table = tomlkit.table()
        doc.add(title, table)
    table[name] = value

    if not path.exists():
        path.parent.mkdir(exist_ok=True, parents=True)

    with open(file=path, mode="w", encoding="UTF-8") as f:
        f.write(tomlkit.dumps(doc))


def load_config_from_file() -> McliConfig:
    path = CONFIG_ROOT_DIR / "mmccli.toml"
    config = McliConfig()

    if not path.exists():
        return config

    with open(file=path, mode="r", encoding="UTF-8") as f:
        doc = tomlkit.parse(f.read())
    for title in doc:
        table: tomlkit.api.Table = doc[title]
        for key, value in table.items():
            key: str
            name = title + "_" + key.replace("-", "_") if title != "mcli" else key.replace("-", "_")
            if hasattr(config, name):
                if name == "log_level":
                    for enum in McliConfig_LogLevel:
                        if value == enum.value:
                            setattr(config, name, enum)
                            break
                else:
                    setattr(config, name, value)
            else:
                warn("配置文件中的无效键 {key} = {value}".format(key=name, value=value))
    return config


useMcliConfig = load_config_from_file()
