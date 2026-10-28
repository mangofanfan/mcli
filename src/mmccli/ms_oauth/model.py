from typing import Literal

from pydantic import BaseModel

from ._model import XboxLiveDisplayClaims


class DeviceFlowResult(BaseModel):
    """Device Flow 登录成功时返回的数据对象"""
    access_token: str
    refresh_token: str
    token_type: Literal["Bearer"]
    expires_in: int
    scope: str
    id_token: str


class XboxLiveResult(BaseModel):
    """Xbox Live 验证成功时返回的数据对象"""
    IssueInstant: str  ## 其实是时间……
    NotAfter: str  ## 其实是时间……
    Token: str
    DisplayClaims: XboxLiveDisplayClaims


class MinecraftServiceAuthResult(BaseModel):
    """Minecraft accessToken 返回的数据对象"""
    username: str
    access_token: str
    token_type: Literal["Bearer"]
    expires_in: int
