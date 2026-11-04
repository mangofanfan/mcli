# mmccli.config.app
import os
import platform
from enum import Enum
from pathlib import Path

import typer
from rich import box
from rich.table import Table

from mmccli.log import console_stdout, info

from .state import useMcliConfig

app = typer.Typer(name="config", help="查看、管理 MCLI 配置")


match platform.system():
    case "Windows":
        ENV_HOME_NAME = "USERPROFILE"
    case _:
        ENV_HOME_NAME = "HOME"
CONFIG_ROOT_DIR = Path(os.environ.get(ENV_HOME_NAME, "")) / ".config" / "mmccli"


@app.command(name="list")
def mmccli_config_list():
    """列出当前生效的 MCLI 配置。"""

    def _render(val):
        if isinstance(val, bool):
            return "✅[green]True[/green]" if val else "❌[red]False[/red]"
        elif isinstance(val, Enum):
            return f"[cyan]Enum([/cyan]{val!s}[cyan])[/cyan]"
        elif isinstance(val, str):
            return f"[cyan]str([/cyan]{val}[cyan])[/cyan]"
        return val

    table = Table(show_header=False, box=box.SIMPLE)
    table.add_column(style="yellow")
    table.add_column(style="white")
    for key, value in useMcliConfig.model_dump().items():
        table.add_row(key, _render(value))
    console_stdout.print(table)


@app.command(name="openfile")
def mmccli_config_openfile():
    """打开 MCLI 配置文件，不存在则先创建。"""
    import subprocess

    CONFIG_ROOT_DIR.mkdir(exist_ok=True, parents=True)
    config_file_path = CONFIG_ROOT_DIR / "mmccli.toml"
    if not config_file_path.exists():
        with open(file=config_file_path, mode="w", encoding="UTF-8") as f:
            f.write("# mmccli/mmccli.toml\n# see https://mango.js.cn/docs/mcli/concept/config\n")
        info("新的 MCLI 配置文件已创建 > {path}".format(path=str(config_file_path)))

    kwargs = {}
    if platform.system() == "Windows":
        kwargs["creationflags"] = subprocess.DETACHED_PROCESS | subprocess.CREATE_NO_WINDOW
        command = "code.cmd"
    else:
        kwargs["start_new_session"] = True
        command = "code"
    subprocess.Popen([command, str(config_file_path)], **kwargs)

    info("已打开 MCLI 配置文件。")
