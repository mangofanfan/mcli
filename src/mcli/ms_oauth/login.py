import requests
from msal import PublicClientApplication

from mcli.log import out
from .error import MicrosoftOauthError
from .model import DeviceFlowResult, XboxLiveResult, MinecraftServiceAuthResult

# Oauth APP 对象
oauthApp = PublicClientApplication(
    client_id="9e9636af-f247-44e0-bd3c-6ad81160266c",
    authority="https://login.microsoftonline.com/consumers",
)


def login_with_microsoft_oauth():
    flow = oauthApp.initiate_device_flow(scopes=["XboxLive.signin", "XboxLive.offline_access"])

    if "user_code" not in flow:
        raise MicrosoftOauthError("发起登录请求失败，原因未知。")

    return flow


def wait_for_access_token(flow: dict):
    result = oauthApp.acquire_token_by_device_flow(flow)
    return DeviceFlowResult.model_validate(result)


def login_for_xbox_live(accessToken: str):
    response = requests.post(
        "https://user.auth.xboxlive.com/user/authenticate",
        json={
            "Properties": {
                "AuthMethod": "RPS",
                "SiteName": "user.auth.xboxlive.com",
                "RpsTicket": "d=" + accessToken,
            },
            "RelyingParty": "http://auth.xboxlive.com",
            "TokenType": "JWT"
        },
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
    )

    data = response.json()
    out(data)
    if response.ok:
        return XboxLiveResult.model_validate(data)
    raise MicrosoftOauthError("验证 Xbox Live 时失败，原因未知。")


def login_for_xsts(xblToken: str):
    response = requests.post(
        "https://xsts.auth.xboxlive.com/xsts/authorize",
        json={
            "Properties": {
                "SandboxId": "RETAIL",
                "UserTokens": [
                    xblToken
                ]
            },
            "RelyingParty": "rp://api.minecraftservices.com/",
            "TokenType": "JWT"
        },
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
    )

    data = response.json()
    out(data)
    if response.ok:
        return XboxLiveResult.model_validate(data)
    raise MicrosoftOauthError("获取 XSTS 令牌时失败，原因未知。")


def login_for_minecraft_with_xsts(uhs: str, xstsToken: str):
    response = requests.post(
        "https://api.minecraftservices.com/authentication/login_with_xbox",
        json={
            "identityToken": f"XBL3.0 x={uhs};{xstsToken}"
        },
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
    )

    data = response.json()
    out(data)
    if response.ok:
        return MinecraftServiceAuthResult.model_validate(data)
    raise MicrosoftOauthError("获取 Minecraft accessToken 时失败，原因未知。")
