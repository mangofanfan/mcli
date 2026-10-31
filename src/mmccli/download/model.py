# mmccli.download.model
import re
from pathlib import Path
from typing import Any

from pydantic import BaseModel

url_re = re.compile(r"^(https?://[a-z0-9.\-:]*)(\S*)$")


class DownloadTask(BaseModel):
    url: str
    url2: str | None = None
    file_path: Path
    cache_file_path: Path | None = None
    size: int | None = None
    sha1: str | None = None

    @property
    def file_name(self):
        return self.file_path.name
