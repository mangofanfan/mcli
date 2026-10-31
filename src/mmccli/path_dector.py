# mmccli.path_dector
from pathlib import Path

from mmccli.log import err, info, useGlobalState, warn


def detect_minecraft_install_folder() -> bool:
    now_path = Path.cwd()

    # 找当前目录
    if now_path.name == ".minecraft":
        useGlobalState.MINECRAFT = now_path
        info(f".minecraft > {now_path!s}")
        return True

    # 找当前目录下的 .minecraft
    for item in now_path.iterdir():
        if item.is_dir() and item.name == ".minecraft":
            useGlobalState.MINECRAFT = item
            # 由于同位置不能有重名目录和文件，所以不需要非空判断
            info(f".minecraft > {item!s}")
            return True

    for parent in now_path.parents:
        if parent.is_dir() and parent.name == ".minecraft":
            useGlobalState.MINECRAFT = parent
            info(f".minecraft > {parent!s}")
            return True

    err("未查找到 Minecraft Java 版游戏安装目录，出于安全考虑任务已终止。")
    warn("如果你需要新建 Minecraft 游戏目录，请首先使用：")
    warn("\tmmccli minecraft init")
    return False
