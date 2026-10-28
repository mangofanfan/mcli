import os

from .logger import console, no

if os.environ.get("MCLI_ENABLE_LOG_OUTPUT", False):
    out = console.log
else:
    out = no
