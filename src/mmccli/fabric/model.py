from typing import Literal

from pydantic import BaseModel, RootModel


class FabricMetaVersions(RootModel[list["FabricMetaVersions_LoaderItem"]]):
    # 支持 for ... in 循环迭代
    def __iter__(self):
        return iter(self.root)

    # 支持通过索引取值，例如 item_list[0]
    def __getitem__(self, item) -> "FabricMetaVersions_LoaderItem":
        return self.root[item]

    # 支持获取长度，例如 len(item_list)
    def __len__(self):
        return len(self.root)


class FabricMetaVersions_LoaderItem(BaseModel):
    loader: "FabricMetaVersions_LoaderItem_Loader"
    intermediary: "FabricMetaVersions_LoaderItem_Intermediary"
    launcherMeta: "FabricMetaVersions_LoaderItem_LauncherMeta"


class FabricMetaVersions_LoaderItem_Loader(BaseModel):
    separator: str
    build: int
    maven: str
    version: str
    stable: bool


class FabricMetaVersions_LoaderItem_Intermediary(BaseModel):
    maven: str
    version: str
    stable: bool


class FabricMetaVersions_LoaderItem_LauncherMeta_MainClass(BaseModel):
    client: str
    server: str


class FabricMetaVersions_LoaderItem_LauncherMeta_Launchwrapper(BaseModel):
    tweakers: dict[Literal["client", "common", "server"], list[str]]


class FabricMetaVersions_LoaderItem_LauncherMeta(BaseModel):
    version: int
    min_java_version: int | None = None
    libraries: "FabricMetaVersions_LoaderItem_LauncherMeta_Libraries"
    mainClass: FabricMetaVersions_LoaderItem_LauncherMeta_MainClass | str
    arguments: dict | None = None
    launchwrapper: FabricMetaVersions_LoaderItem_LauncherMeta_Launchwrapper | None = None


class FabricMetaVersions_LoaderItem_LauncherMeta_Libraries(BaseModel):
    client: list["FabricMetaVersions_LoaderItem_LauncherMeta_LibraryItem"]
    common: list["FabricMetaVersions_LoaderItem_LauncherMeta_LibraryItem"]
    server: list["FabricMetaVersions_LoaderItem_LauncherMeta_LibraryItem"]
    development: list["FabricMetaVersions_LoaderItem_LauncherMeta_LibraryItem"] | None = None


class FabricMetaVersions_LoaderItem_LauncherMeta_LibraryItem(BaseModel):
    name: str
    url: str | None = None
    md5: str | None = None
    sha1: str | None = None
    sha256: str | None = None
    sha512: str | None = None
    size: int | None = None
