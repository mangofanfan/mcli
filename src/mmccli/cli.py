# mmccli.cli


__all__ = ["main"]


def on_startup():
    from importlib.metadata import version

    from dotenv import load_dotenv

    _dev_version = version("mmccli").find("dev") > 0
    if _dev_version:
        load_dotenv()

    from importlib import resources
    from random import choice

    from rich.panel import Panel

    from mmccli.log import console

    with open(file=str(resources.files("mmccli").joinpath("assets/hitokoto.txt")), mode="r", encoding="UTF-8") as f:
        line = choice(f.readlines())
    console.print(f"[#748cab]MCLI >[/#748cab] [#b5c99a]{line.strip()}[/#b5c99a]")

    if _dev_version:
        panel = Panel(
            "正在运行 MCLI [yellow]开发中版本[/yellow]，[red]工作区环境变量[/red]会自动加载。\n"
            "MCLI-MMCCLI [yellow]{version}[/yellow]".format(version=version("mmccli")),
            title="Dev-Version Warning",
            title_align="left",
            border_style="yellow",
        )
        console.print(panel)
        load_dotenv()


def main():
    on_startup()

    from .app import app

    app()
