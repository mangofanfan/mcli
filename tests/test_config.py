import os
from pathlib import Path


def test_mmccli_config_list(runner, app):
    result = runner.invoke(app, ["config", "list"])

    assert result.exit_code == 0

    items = result.stdout.splitlines()[1:-1]
    # 颜色代码就不测了吧？
    assert "log-level" in items[0] and "McliConfig_LogLevel.INFO" in items[0]


def test_mmccli_config_from_env(runner, app):
    result = runner.invoke(
        app,
        ["config", "list"],
        env={
            "MCLI_LOG_LEVEL": "DEBUG",
            "MCLI_NO_PROXY": "False",
            "MCLI_NO_SSL_VERIFY": "False",
        },
    )

    assert result.exit_code == 0

    items = result.stdout.splitlines()[1:-1]
    assert "log-level" in items[0] and "McliConfig_LogLevel.DEBUG" in items[0]
    assert "no-proxy" in items[1] and "False" in items[1]
    assert "no-ssl-verify" in items[2] and "False" in items[2]


def test_mmccli_config_from_args(runner, app):
    result = runner.invoke(
        app,
        ["--log-level", "DEBUG", "config", "list"],
        env={"MCLI_LOG_LEVEL": "WARNING"},
    )

    assert result.exit_code == 0

    items = result.stdout.splitlines()[1:-1]
    assert "log-level" in items[0] and "McliConfig_LogLevel.DEBUG" in items[0]


def test_mmccli_config_from_toml(runner, app, caplog):
    expected_path = Path(os.environ["MCLI_CONTEXT_CONFIG_DIR"]) / "mmccli.toml"
    caplog.set_level("INFO", logger="rich")

    result = runner.invoke(
        app,
        ["config", "list"],
    )

    assert result.exit_code == 0

    # 路径通过 logging 输出；检查原始日志消息，避免 Rich 标记和换行的影响。
    config_path_messages = [message for message in caplog.messages if "正在使用的 MCLI 配置文件" in message]
    assert len(config_path_messages) == 1
    assert str(expected_path) in config_path_messages[0]

    runner.invoke(
        app,
        ["config", "set", "log-level", "WARNING"],
    )
    runner.invoke(
        app,
        ["config", "set", "editor", "code.cmd"],
    )
    config_file_content = """# mmccli/mmccli.toml
# see https://mango.js.cn/docs/mcli/concept/config
# If you cannot find where this file: {path!s}

[mcli]
log-level = "WARNING"
editor = "code.cmd"
""".format(path=expected_path)
    with open(expected_path, "r") as f:
        assert config_file_content in f.read()

    result = runner.invoke(
        app,
        ["--editor", "notepad.exe", "config", "list"],
        env={
            "MCLI_LOG_LEVEL": "DEBUG",
        },
    )

    assert result.exit_code == 0

    items = result.stdout.splitlines()[1:-1]
    assert "log-level" in items[0] and "McliConfig_LogLevel.DEBUG" in items[0]
    assert "editor" in items[3] and "notepad.exe" in items[3]
