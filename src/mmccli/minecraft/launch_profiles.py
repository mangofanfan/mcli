# mmccli.minecraft.launch_profiles
from mmccli.log import out, useGlobalState

from .model import McGameVersionJson, McLauncherLaunchProfilesJson, McLauncherLaunchProfilesJson_ProfilesItem


def save_launcher_profiles_json(mc_version_json: McGameVersionJson):
    from datetime import datetime
    from uuid import uuid4

    key = uuid4().hex
    now = datetime.now()

    # 已有启动器配置文件就写入，否则新建
    if not useGlobalState.MINECRAFT:
        raise RuntimeError(f"Unexpected value of {useGlobalState.MINECRAFT=}")
    file_path = useGlobalState.MINECRAFT / "launcher_profiles.json"
    file_path.parent.mkdir(exist_ok=True, parents=True)
    profile = McLauncherLaunchProfilesJson_ProfilesItem(
        created=now.isoformat(),
        icon="Grass",
        javaArgs="-Xms2G -Xmx4G -XX:+UseCompactObjectHeaders -XX:+AlwaysPreTouch -XX:+UseStringDeduplication -XX:+UseZGC",
        lastUsed="1970-01-01T00:00:00.000Z",
        lastVersionId=mc_version_json.id,
        name=mc_version_json.id,
        type="custom",
    )
    if file_path.exists():
        with open(file=file_path, mode="r") as f:
            launcher_profiles = McLauncherLaunchProfilesJson.model_validate_json(f.read())
            launcher_profiles.profiles[key] = profile
    else:
        launcher_profiles = McLauncherLaunchProfilesJson(
            profiles={key: profile},
            settings={},
            version=6,
        )
    with open(file=file_path, mode="w", encoding="UTF-8") as f:
        f.write(launcher_profiles.model_dump_json(indent=4, exclude_unset=True))
    out("已更新或新建启动器配置 json 文件。")


def write_default_launcher_profiles_json():
    if not useGlobalState.MINECRAFT:
        raise RuntimeError(f"Unexpected value of {useGlobalState.MINECRAFT=}")
    file_path = useGlobalState.MINECRAFT / "launcher_profiles.json"
    file_path.parent.mkdir(exist_ok=True, parents=True)
    with open(file=file_path, mode="w", encoding="UTF-8") as f:
        f.write(McLauncherLaunchProfilesJson(profiles={}, settings={}, version=6).model_dump_json(indent=4))
    out("已新建默认启动器配置 json 文件。")
