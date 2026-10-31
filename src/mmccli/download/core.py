# mmccli.download.core
import asyncio
import hashlib
import os

import aiofiles
from aiohttp import ClientSession

from mmccli.cache import link_or_move
from mmccli.log import err, out, useGlobalState, warn

from .error import HashVerifyError
from .model import DownloadTask

__all__ = ["async_download_task", "async_download_tasks"]

headers = {"User-Agent": "MCLI-MMCCLI/0.2.0-alpha (+https://mango.js.cn/mcli) aiohttp/3.14.5"}


async def async_download_tasks(download_tasks: list[DownloadTask], sem_max: int):
    session = ClientSession(headers=headers)
    sem = asyncio.Semaphore(sem_max)

    error_tasks: list[DownloadTask] = []
    out(f"async - 异步开始 {len(download_tasks)} 个下载任务。")

    for result in asyncio.as_completed(
        [asyncio.create_task(_async_start_download(session, task, sem)) for task in download_tasks]
    ):
        success, task, errs = await result
        useGlobalState.DOWNLOAD_TASK_DOING -= 1
        if not success:
            useGlobalState.DOWNLOAD_TASK_FAIL += 1
            error_tasks.append(task)
            await _async_log_errs(task, errs)
        else:
            useGlobalState.DOWNLOAD_TASK_COMPLETE += 1

    useGlobalState.DOWNLOAD_CONTINUE = False
    await session.close()


async def async_download_task(download_task: DownloadTask):
    session = ClientSession(headers=headers)
    success, _, errs = await _async_download(session, download_task)
    if not success:
        await _async_log_errs(download_task, errs)

    useGlobalState.DOWNLOAD_CONTINUE = False
    await session.close()


async def _async_start_download(
    session: ClientSession, task: DownloadTask, sem: asyncio.Semaphore
) -> tuple[bool, DownloadTask, list[Exception]]:
    async with sem:
        return await _async_download(session, task)


async def _async_download(session: ClientSession, task: DownloadTask) -> tuple[bool, DownloadTask, list[Exception]]:
    task.file_path.parent.mkdir(exist_ok=True, parents=True)
    if task.cache_file_path:
        task.cache_file_path.parent.mkdir(exist_ok=True, parents=True)

    save_path = task.cache_file_path if task.cache_file_path else task.file_path
    ok = False
    errs: list[Exception] = []

    async def _download(iter_count: int):
        # 两次尝试 url，一次尝试 url2，然后报错
        response = await session.get(url=task.url2 if iter_count == 2 and task.url2 else task.url, ssl=False)
        response.raise_for_status()
        if response.ok:
            async with aiofiles.open(file=save_path, mode="wb") as af:
                async for chunk in response.content.iter_chunked(1_048_576):
                    useGlobalState.DOWNLOAD_SIZE_COMPLETE += len(chunk)
                    await af.write(chunk)

    async def _verify():
        if save_path.is_file():
            file_sha1 = hashlib.sha1()
            async with aiofiles.open(file=save_path, mode="rb") as af:
                while True:
                    chunk = await af.read(1_048_576)
                    if not chunk:
                        break
                    file_sha1.update(chunk)
            if task.sha1 != file_sha1.hexdigest():  # 校验失败时删除文件，以在下一次循环触发下载
                os.remove(save_path)
                raise HashVerifyError(task=task, existed_sha1=file_sha1.hexdigest())
        else:
            raise RuntimeError(f"Uncreated file {task.file_path!s} should not appear ?")

    for i in range(3):
        try:
            if not save_path.exists():
                await _download(i)
            if task.sha1:  # 有的玩意没有散列值可供校验，对说的就是 Fabric
                await _verify()
            if task.cache_file_path:
                link_or_move(task.cache_file_path, task.file_path)
            ok = True
        except Exception as e:
            warn(f"async - {task.file_name} 下载出现异常，还剩 {2 - i} 次尝试 | {e!s}")
            errs.append(e)
            if 2 - i > 0:
                continue
            else:
                break

    if ok:
        out(f"async - {task.file_name} 下载完成。")
        return True, task, errs
    else:
        err(f"async - {task.file_name} 下载失败。")
        return False, task, errs


async def _async_log_errs(task: DownloadTask, errs: list[Exception]):
    async with aiofiles.open(file="error-tasks.mmccli-download.log", mode="a", encoding="UTF-8") as af:
        await af.write(f"file_path: {task.file_path!s}\n")
        await af.write(f"url: {task.url}\n")
        await af.write(f"url2: {task.url2}\n")
        await af.write(f"err: 1: {errs[0]!s}\n")
        await af.write(f"err: 2: {errs[1]!s}\n")
        await af.write(f"err: 3: {errs[2]!s}\n\n")
