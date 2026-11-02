# mmccli
from importlib.metadata import version

from .app import app

__version__ = version("mmccli")

__all__ = [
    "__version__",
    "app",
]
