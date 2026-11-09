# mmccli
from importlib.metadata import version

from .app import app as mmccli

__version__ = version("mmccli")

__all__ = [
    "__version__",
    "mmccli",
]
