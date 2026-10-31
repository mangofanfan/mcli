from rich.repr import Result as RichReprResult

from mmccli.download.model import DownloadTask


class HashVerifyError(Exception):
    def __init__(self, task: DownloadTask, existed_sha1: str):
        super().__init__()
        self.task = task
        self.existed_sha1 = existed_sha1

    def __rich_repr__(self) -> RichReprResult:
        yield f"(MMCCLI) HashVerifyError of {self.task.file_name}"
        yield "url", self.task.url
        yield "url2", self.task.url2
        yield "file_path", self.task.file_path
        yield "cache_file_path", self.task.cache_file_path
        yield "size", self.task.size
        yield "sha1", self.task.sha1
        yield "existed_sha1", self.existed_sha1
