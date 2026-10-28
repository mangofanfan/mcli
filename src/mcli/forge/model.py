# mcli.forge.model
from typing import Any, Literal

from pydantic import BaseModel, Field, RootModel, model_validator

from mcli.minecraft import McGameVersionJson_Arguments, McGameVersionJson_LibrariesItem


class ForgeInstallerVersionJson(BaseModel):
    _comment: list[str]
    id: str
    time: str
    releaseTime: str
    inheritsFrom: str  # Minecraft 本体版本
    type: Literal["release", "snapshot"]
    mainClass: str
    libraries: list[McGameVersionJson_LibrariesItem]
    arguments: McGameVersionJson_Arguments


class ForgeInstallerInstallProfileJson(BaseModel):
    _comment: list[str]
    spec: int
    hideExtract: bool
    profile: Literal["forge"]
    version: str
    path: str
    minecraft: str  # Minecraft 本体版本
    serverJarPath: str
    data: Any
    processors: Any
    libraries: list[McGameVersionJson_LibrariesItem]
    icon: str  # Base64 编码的信息
    json_data: str = Field(alias="json")  # /version.json
    logo: str  # /big_logo.png
    mirrorList: str
    welcome: str  # Welcome to the Forge installer.


class ForgePromosListJson(RootModel[list["ForgePromosListJson_Item"]]):
    # 支持 for ... in 循环迭代
    def __iter__(self):
        return iter(self.root)

    # 支持通过索引取值，例如 item_list[0]
    def __getitem__(self, item) -> "ForgePromosListJson_Item":
        return self.root[item]

    # 支持获取长度，例如 len(item_list)
    def __len__(self):
        return len(self.root)

    @model_validator(mode="before")
    @classmethod
    def filter_out_null_build(cls, data):
        # 确保输入是列表类型，然后过滤掉 build 为 None 的项
        if isinstance(data, list):
            # 使用列表推导式，静默跳过 build 为 None 的字典
            return [item for item in data if not (isinstance(item, dict) and item.get("build") is None)]
        return data


class ForgeVersionListJson(RootModel[list["ForgeVersionItem"]]):
    # 支持 for ... in 循环迭代
    def __iter__(self):
        return iter(self.root)

    # 支持通过索引取值，例如 item_list[0]
    def __getitem__(self, item) -> "ForgeVersionItem":
        return self.root[item]

    # 支持获取长度，例如 len(item_list)
    def __len__(self):
        return len(self.root)


class ForgePromosListJson_Item(BaseModel):
    _id: str
    __v: int
    name: str
    build: "ForgeVersionItem"


class ForgeVersionItem(BaseModel):
    _id: str
    __v: int
    build: int  # Forge 构建
    files: list["ForgeVersionItem_FilesItem"]
    mcversion: str  # MC 本体版本
    modified: str
    version: str  # Forge 版本号


class ForgeVersionItem_FilesItem(BaseModel):
    format: Literal["txt", "jar", "zip"]
    category: str
    hash: str


class ForgeInstallerVersionInfo(BaseModel):
    """MCLI 使用"""
    id: str  # 安装器版本的人类可读模式，例如 62.0.1
    name: str  # 安装器的人类可读名称，例如 forge-installer-26.1-62.0.1.jar
    build: int
    hash: str
