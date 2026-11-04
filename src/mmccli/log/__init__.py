# mmccli.log

# 导入顺序不可更改

from .error import RequestStatusError
from .logger import console, console_stdout, err, info, out, warn
from .state import useGlobalState

__all__ = [
    "RequestStatusError",
    "console",
    "console_stdout",
    "err",
    "info",
    "out",
    "useGlobalState",
    "warn",
]
