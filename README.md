# Minecraft \(Java Edition Manager in\) Commandline

> Minecraft Java 版命令行管理工具，简写为 MCLI。

这是一个使用 Python 实现的命令行工具，用于管理 Minecraft Java 版的版本实例。

或者简单来说是一个下载器。

**MCLI 不是一款 Minecraft 启动器，你仍然需要一个启动器来启动本工具添加的版本。**

## 特色

MCLI 致力于实现类似于*包管理器*的使用体验。

* 依赖库文件、资源文件等全局缓存，在游戏目录中硬链接。
* 多任务、多线程并发下载，提高下载速度（也许）。
* 可配置镜像源，提高下载速度（也许）。

并且不只是下载游戏本体，MCLI 还支持：

* 添加模组加载器。
  * 已支持 1.13+ Forge、Fabric，启动器可识别与启动。
  * 正在计划支持 NeoForge 和 Quilt（这个还在更新吗？）

未来 MCLI 还长期计划：

* 支持一行命令从 CurseForge 和/或 Modrinth 安装模组。
* 支持一行命令安装服务器。
* 使用更快速的方式重新实现下载功能。

## 使用

### 安装（或者不安装）

```shell
uvx mcli <command>

# 或者安装为工具，然后直接使用
uv tool install mcli
mcli <command>
```

### 添加游戏

```shell
mcli add --minecraft 26.1
mcli add --minecraft 26.2 --forge latest
mcli add --minecraft 26.3 --name "原版 26.3"
```
