# mmccli.config.app
from enum import Enum

import typer
from rich import box
from rich.table import Table

from mmccli.log import console_stdout

from .state import useMcliConfig

app = typer.Typer(name="config", help="查看、管理 MCLI 配置")


@app.command(name="list")
def mmccli_config_list():
    """列出当前生效的 MCLI 配置。"""

    def _render(val):
        if isinstance(val, bool):
            return "✅[green]True[/green]" if val else "❌[red]False[/red]"
        elif isinstance(val, Enum):
            return f"[cyan]Enum([/cyan]{val}[cyan])[/cyan]"
        elif isinstance(val, str):
            return f"[cyan]str([/cyan]{val!s}[cyan])[/cyan]"
        return val

    table = Table(show_header=False, box=box.SIMPLE)
    table.add_column(style="yellow")
    table.add_column(style="white")
    for key, value in useMcliConfig.model_dump().items():
        table.add_row(key, _render(value))
    console_stdout.print(table)
