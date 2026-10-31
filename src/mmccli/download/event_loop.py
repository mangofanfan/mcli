# mmccli.download.event_loop
import asyncio
from threading import Thread

from mmccli.log import out, useGlobalState

from .core import async_download_task, async_download_tasks
from .model import DownloadTask


def thread_start_event_loop_and_download_tasks(download_tasks: list[DownloadTask], sem_max: int):
    asyncio.run(async_download_tasks(download_tasks, sem_max))


def thread_start_event_loop_and_download_task(download_task: DownloadTask):
    asyncio.run(async_download_task(download_task))


def start_download_tasks(download_tasks: list[DownloadTask], sem_max: int = 32):
    """批量下载多个文件"""
    useGlobalState.DOWNLOAD_TASK_DOING = len(download_tasks)
    thread = Thread(
        target=thread_start_event_loop_and_download_tasks,
        kwargs={"download_tasks": download_tasks, "sem_max": sem_max},
        name="Thread-AsyncDownloader",
    )
    thread.start()
    out("已派遣子线程负责多文件异步下载。")
    useGlobalState.DOWNLOAD_CONTINUE = True
    return thread


def start_download_task(download_task: DownloadTask):
    """下载单个文件"""
    useGlobalState.DOWNLOAD_TASK_DOING = 1
    thread = Thread(
        target=thread_start_event_loop_and_download_task,
        kwargs={"download_task": download_task},
        name="Thread-AsyncDownloader",
    )
    thread.start()
    out("已派遣子线程负责单文件下载。")
    useGlobalState.DOWNLOAD_CONTINUE = True
    return thread
