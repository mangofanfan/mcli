from mmccli import mmccli


def test_mmccli_config_list(runner):
    result = runner.invoke(mmccli, ["config", "list"])

    assert result.exit_code == 0

    items = result.stdout.splitlines()[1:-1]
    # 颜色代码就不测了吧？
    assert "log-level" in items[0] and "McliConfig_LogLevel.INFO" in items[0]


def test_mmccli_config_from_env(runner):
    result = runner.invoke(
        mmccli,
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


def test_mmccli_config_from_args(runner):
    result = runner.invoke(
        mmccli,
        ["--log-level", "DEBUG", "config", "list"],
        env={"MCLI_LOG_LEVEL": "WARNING"},
    )

    assert result.exit_code == 0

    items = result.stdout.splitlines()[1:-1]
    assert "log-level" in items[0] and "McliConfig_LogLevel.DEBUG" in items[0]
