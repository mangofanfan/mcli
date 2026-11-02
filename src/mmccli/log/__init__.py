# mmccli.log

import os

from .error import RequestStatusError
from .gateway import out
from .logger import console, err, info, raw, warn
from .state import useGlobalState

if os.environ.get("MCLI_ENABLE_LOG_OUTPUT", None):
    out("日志输出已启用（通过环境变量 MCLI_ENABLE_LOG_OUTPUT）")

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
    "raw",
    "useGlobalState",
    "warn",
]
