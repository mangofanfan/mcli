import os
import shutil
from pathlib import Path

import pytest
from typer.testing import CliRunner


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture(scope="session")
def app():
    mmccli_dir = Path(__file__).parent / ".mmccli"
    config_dir = mmccli_dir / "config"
    mmccli_dir.mkdir(exist_ok=False)
    config_dir.mkdir(exist_ok=False)

    os.environ["MCLI_CONTEXT_CONFIG_DIR"] = str(config_dir)
    os.environ["MCLI_CONTEXT_MMCCLI_DIR"] = str(mmccli_dir)
    from mmccli.app import app as mmccli

    yield mmccli
    os.environ["MCLI_CONTEXT_CONFIG_DIR"] = ""
    os.environ["MCLI_CONTEXT_MMCCLI_DIR"] = ""

    shutil.rmtree(mmccli_dir)
