from typing import Literal

from pydantic import BaseModel


class McGameVersionManifestV2VersionItem(BaseModel):
    id: str
    type: Literal["snapshot", "release", "old_alpha", "old_beta"]
    url: str
    time: str
    releaseTime: str
    sha1: str
    complianceLevel: int


class McGameVersionJson_FileModel(BaseModel):
    url: str
    size: int | None
    sha1: str | None


class McGameVersionJson_LibrariesItemDownloadsArtifact(McGameVersionJson_FileModel):
    path: str


class McGameVersionJson_LibrariesItemDownloads(BaseModel):
    artifact: McGameVersionJson_LibrariesItemDownloadsArtifact


class McGameVersionJson_LoggingItemFile(McGameVersionJson_FileModel):
    id: str


class McGameVersionJson_RuleOsVersionRange(BaseModel):
    min: str | None = None
    max: str | None = None


class McGameVersionJson_RuleOs(BaseModel):
    name: Literal["osx", "linux", "windows"] | None = None
    arch: Literal["x86"] | None = None
    versionRange: McGameVersionJson_RuleOsVersionRange | None = None


class McGameVersionJson_Rule(BaseModel):
    action: Literal["allow"]
    os: McGameVersionJson_RuleOs | None = None
    features: dict[str, bool] | None = None


class McGameAssetIndexJson_ObjectsItem(BaseModel):
    hash: str
    size: int
