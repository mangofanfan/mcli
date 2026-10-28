# mcli.log.state
from pathlib import Path


class State:
    def __init__(self):
        self.HARDLINK_DOWNGRADE_TO_FULL_COPY: bool = False

        self.MINECRAFT: Path | None = None


useGlobalState = State()
