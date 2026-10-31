# mmccli.log.logger
from rich.console import Console
from rich.style import Style
from rich.text import Text

console = Console()


def info(message: str):
    console.print(Text(text="▶ ", style=Style(color="green")) + Text(text=message, style=Style(color="#90e0ef")))


def warn(message: str):
    console.print(Text(text="⁜ ", style=Style(color="yellow")) + Text(text=message, style=Style(color="#e9c46a")))


def err(message: str):
    console.print(Text(text="✕ ", style=Style(color="red")) + Text(text=message, style=Style(color="#e76f51")))


def raw(message):
    console.print(message)


def no(message):
    pass
