# mmccli.log.state
from pathlib import Path


class State:
    def __init__(self):
        self.HARDLINK_DOWNGRADE_TO_FULL_COPY: bool = False

        self.MINECRAFT: Path | None = None

        self.DOWNLOAD_CONTINUE: bool = False
        self.DOWNLOAD_TASK_DOING: int = 0
        self.DOWNLOAD_TASK_COMPLETE: int = 0
        self.DOWNLOAD_TASK_FAIL: int = 0
        self.DOWNLOAD_SIZE_COMPLETE: int = 0

    def clear_download_status(self):
        self.DOWNLOAD_CONTINUE = False
        self.DOWNLOAD_TASK_DOING = 0
        self.DOWNLOAD_TASK_COMPLETE = 0
        self.DOWNLOAD_TASK_FAIL = 0
        self.DOWNLOAD_SIZE_COMPLETE = 0


useGlobalState = State()
