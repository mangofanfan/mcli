from enum import Enum

__all__ = [
    "McliConfig_LogLevel",
]


class McliConfig_LogLevel(str, Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
