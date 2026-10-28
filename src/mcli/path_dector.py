# mcli.path_dector
from pathlib import Path

from mcli.log import err, useGlobalState


def detect_minecraft_install_folder() -> bool:
    now_path = Path.cwd()

    # 找当前目录
    if now_path.name == ".minecraft":
        useGlobalState.MINECRAFT = now_path
        return True

    # 找当前目录下的 .minecraft
    for item in now_path.iterdir():
        if item.is_dir() and item.name == ".minecraft":
            useGlobalState.MINECRAFT = item
            # 由于同位置不能有重名目录和文件，所以不需要非空判断
            return True

    for parent in now_path.parents:
        if parent.is_dir() and parent.name == ".minecraft":
            useGlobalState.MINECRAFT = parent
            return True

    err("未查找到 Minecraft Java 版游戏安装目录。")
    return False
