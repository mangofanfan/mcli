# mmccli.config.app

import platform
from enum import Enum
from typing import Annotated

import typer
from rich import box
from rich.table import Table

from mmccli.log import console_stdout, err, info

from .config_item import McliConfig_LogLevel
from .state import CONFIG_ROOT_DIR, McliConfig, save_config_to_file, useMcliConfig

app = typer.Typer(name="config", help="查看、管理 MCLI 配置")


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
        table.add_row(key.replace("_", "-"), _render(value))
    console_stdout.print(table)


@app.command(name="openfile")
def mmccli_config_openfile():
    """打开 MCLI 配置文件。"""
    import subprocess

    CONFIG_ROOT_DIR.mkdir(exist_ok=True, parents=True)
    config_file_path = CONFIG_ROOT_DIR / "mmccli.toml"

    kwargs = {}
    if platform.system() == "Windows":
        kwargs["creationflags"] = subprocess.DETACHED_PROCESS | subprocess.CREATE_NO_WINDOW
        command = "code.cmd"
    else:
        kwargs["start_new_session"] = True
        command = "code"

    if not config_file_path.exists():
        save_config_to_file("log_level", "INFO")
    subprocess.Popen([command, str(config_file_path)], **kwargs)

    info("已打开 MCLI 配置文件。")


@app.command(name="set")
def mmccli_config_set(
    key: Annotated[str, typer.Argument(help="配置键")],
    value: Annotated[str, typer.Argument(help="配置值")],
):
    """配置 MCLI。"""
    if "_" in key:
        err("{key} 不是合法的配置键名。".format(key=key))
        raise typer.Exit(400)

    inner_key = key.replace("-", "_")
    if inner_key in useMcliConfig.model_dump():
        success = False
        if value == "True":
            save_config_to_file(inner_key, True)
            success = True
        elif value == "False":
            save_config_to_file(inner_key, False)
            success = True

        if inner_key == "log_level":
            for level in McliConfig_LogLevel:
                if level.value == value:
                    save_config_to_file(inner_key, value)
                    success = True
                    continue

        if not success:
            save_config_to_file(inner_key, value)
        info("{key} 已设置。".format(key=key))
    else:
        err("{key} 不是合法的配置键名。".format(key=key))
        raise typer.Exit(400)
