from pydantic import BaseModel


class XboxLiveDisplayClaimsXuiItem(BaseModel):
    uhs: str


class XboxLiveDisplayClaims(BaseModel):
    xui: list[XboxLiveDisplayClaimsXuiItem]
