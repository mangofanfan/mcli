# mmccli.log.logger
import logging
import os

import rich
import typer
from rich.console import Console
from rich.logging import RichHandler

# console 是输出到标准错误的控制台，用于大部分内容，包括日志
# console_stdout 是输出到标准输出的控制台，用于返回有效信息
console = Console(highlight=False, stderr=True)
console_stdout = Console(highlight=False)

logging.basicConfig(
    level=os.environ.get("MCLI_LOG_LEVEL", "INFO"),
    format="%(message)s",
    datefmt="[%X]",
    handlers=[
        RichHandler(
            omit_repeated_times=False,
            rich_tracebacks=True,
            tracebacks_suppress=[typer, rich],
            console=console,
            show_path=False,
        )
    ],
)

logger = logging.getLogger("rich")


out = logger.debug
info = logger.info
warn = logger.warning
err = logger.error
