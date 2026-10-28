from rich.console import Console

console = Console()


def info(message: str):
    console.print("[green]▶[/green] " + message)


def warn(message: str):
    console.print("[yellow]⁜[/yellow] " + message)


def err(message: str):
    console.print("[red]✕[/red] " + message)


def raw(message):
    console.print(message)


def no(message):
    pass
