# mmccli.minecraft.model

from typing import Any, Literal

from pydantic import BaseModel, Field

from ._model import (
    McGameAssetIndexJson_ObjectsItem,
    McGameVersionJson_FileModel,
    McGameVersionJson_LibrariesItemDownloads,
    McGameVersionJson_LoggingItemFile,
    McGameVersionJson_Rule,
    McGameVersionManifestV2VersionItem,
)


class McGameVersionManifestV2(BaseModel):
    latest: dict[Literal["release", "snapshot"], str]
    versions: list[McGameVersionManifestV2VersionItem]


class McGameVersionJson_ArgumentsItem(BaseModel):
    value: list[str] | str
    rules: list[McGameVersionJson_Rule] | None = None


class McGameVersionJson_LibrariesItem(BaseModel):
    downloads: McGameVersionJson_LibrariesItemDownloads
    name: str
    rules: list[McGameVersionJson_Rule] | None = None


class McGameVersionJson_Arguments(BaseModel):
    default_user_jvm: list[McGameVersionJson_ArgumentsItem] | None = Field(alias="default-user-jvm", default=None)
    game: list[McGameVersionJson_ArgumentsItem | str]
    jvm: list[McGameVersionJson_ArgumentsItem | str]


class McGameVersionJson_AssetIndex(McGameVersionJson_FileModel):
    id: str
    totalSize: int


class McGameVersionJson_LoggingItem(BaseModel):
    argument: str
    file: McGameVersionJson_LoggingItemFile
    type: str


class McGameVersionJson_JavaVersion(BaseModel):
    component: str
    majorVersion: int


class McGameVersionJson(BaseModel):
    arguments: McGameVersionJson_Arguments
    assetIndex: McGameVersionJson_AssetIndex
    assets: str
    complianceLevel: int
    downloads: dict[Literal["client", "server", "client_mappings", "server_mappings"], McGameVersionJson_FileModel]
    id: str
    javaVersion: McGameVersionJson_JavaVersion
    libraries: list[McGameVersionJson_LibrariesItem]
    logging: dict[Literal["client"], McGameVersionJson_LoggingItem]
    mainClass: str
    minimumLauncherVersion: int
    releaseTime: str
    time: str
    type: Literal["release", "snapshot"]


class McGameAssetIndexJson(BaseModel):
    objects: dict[str, McGameAssetIndexJson_ObjectsItem]


class McLauncherLaunchProfilesJson_ProfilesItem(BaseModel):
    created: str | None = None
    icon: str
    javaArgs: str | None = None
    lastUsed: str | None = None
    lastVersionId: str
    name: str
    type: Literal["latest-release", "latest-snapshot", "custom"]


class McLauncherLaunchProfilesJson(BaseModel):
    profiles: dict[str, McLauncherLaunchProfilesJson_ProfilesItem] | None = {}
    settings: dict[str, Any] | None = {}
    version: int | None = 6
