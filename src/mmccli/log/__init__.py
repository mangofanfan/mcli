# mmccli.log

import os

from .error import RequestStatusError
from .logger import console, err, info, out, warn
from .state import useGlobalState

if level := os.environ.get("MCLI_LOG_LEVEL", "INFO"):
    out(f"日志输出等级设置为 {level}。")

    if os.environ.get("MCLI_SKIP_ONLINE_AUTH", None):
        out("跳过正版验证已启用（通过环境变量 MCLI_SKIP_ONLINE_AUTH）")

    if os.environ.get("MCLI_NO_PROXY", None):
        os.environ["HTTP_PROXY"] = ""
        os.environ["HTTPS_PROXY"] = ""
        out("忽视网络代理已启用（通过环境变量 MCLI_NO_PROXY）")
    if os.environ.get("HTTP_PROXY", None):
        out("HTTP_PROXY 环境变量已设置，代理将在网络请求中应用。")
    if os.environ.get("HTTPS_PROXY", None):
        out("HTTPS_PROXY 环境变量已设置，代理将在网络请求中应用。")
    if os.environ.get("MCLI_NO_SSL_VERIFY", None):
        out("SSL 验证已关闭（通过环境变量 MCLI_SSL_VERIFY）")

__all__ = [
    "RequestStatusError",
    "console",
    "err",
    "info",
    "out",
    "useGlobalState",
    "warn",
]
