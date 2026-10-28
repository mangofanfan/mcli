# mmccli.forge.install
from rich.live import Live

from mmccli.forge.model import ForgeInstallerVersionJson
from mmccli.log import console, out, useGlobalState, warn


def install_forge_silently(forge_installer_path: str, minecraft_path: str):
    """静默安装 Forge，应该是仅支持 1.13+"""
    import subprocess
    from importlib import resources

    forge_install_tool_path = resources.files("mmccli").joinpath("bin/forge-install-bootstrapper.jar")

    command = " ".join(
        [
            "java",
            "-cp",
            f"{forge_install_tool_path};{forge_installer_path}",
            "com.bangbang93.ForgeInstaller",
            minecraft_path,
        ]
    )
    out(f"准备执行 Forge 安装命令 | {command}")

    process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
    )

    with Live("[cyan]<l>[/cyan] [black]正在安装 Forge[/black]", console=console) as live:
        while True:
            line = process.stdout.readline()  # type: ignore[union-attr]

            if line == "" and process.poll() is not None:
                out("子进程退出，安装结束。")
                break  # 安装进程已结束

            if line:
                live.update(f"[cyan]<installing forge>[/cyan] [black]{line.strip()}[/black]")

    result = process.wait()
    if result != 0:
        warn("Forge 安装失败。")
    return result == 0


def rename_forge_version(vanilla_version_id: str, forge_version_id: str, name: str):
    """将 Forge 安装器静默安装生成的版本名称（26.2-forge-65.1.5）重命名成用户设置的"""
    if not useGlobalState.MINECRAFT:
        raise RuntimeError(f"Unexpected None of {useGlobalState.MINECRAFT=}")
    default_name = vanilla_version_id + "-forge-" + forge_version_id
    default_version_folder = useGlobalState.MINECRAFT / "versions" / default_name
    default_version_json_path = default_version_folder / (default_name + ".json")
    target_version_folder = useGlobalState.MINECRAFT / "versions" / name
    target_version_json_path = target_version_folder / (name + ".json")

    with open(file=default_version_json_path, mode="r", encoding="UTF-8") as f:
        forge_version_json = ForgeInstallerVersionJson.model_validate_json(f.read())
    forge_version_json.id = name
    target_version_folder.mkdir(exist_ok=False, parents=True)
    with open(file=target_version_json_path, mode="w", encoding="UTF-8") as f:
        f.write(forge_version_json.model_dump_json(indent=4))
    out(f"已重命名 Forge 安装至 {name}")
