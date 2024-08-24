# -*- coding: utf-8 -*-

__author__ = "yanyongyu & Eilles"


from contextlib import asynccontextmanager
from typing import AsyncIterator

from pyppeteer.browser import Browser, Page
from nonebot import get_plugin_config

from liteyuki.log import logger


from .config import Config

config = get_plugin_config(Config)

from src.utils.htmlrender.control import (
    _browser,
    init as launch_browser,
    shutdown_browser,
)


_playwright = True


async def init(**kwargs) -> Browser:

    if config.htmlrender_proxy_host:
        kwargs["arg"] = {
            "proxy-server": config.htmlrender_proxy_host,
        }

    return await launch_browser(**kwargs)


async def get_browser(**kwargs) -> Browser:
    return (
        _browser
        if _browser and _browser._connection._connected
        else await init(**kwargs)
    )


@asynccontextmanager
async def get_new_page(device_scale_factor: float = 2, **kwargs) -> AsyncIterator[Page]:

    if device_scale_factor:
        if "viewport" not in kwargs:
            kwargs["viewport"] = {
                "deviceScaleFactor": device_scale_factor,
            }
        else:
            kwargs["viewport"]["deviceScaleFactor"] = device_scale_factor

    browser = await get_browser()
    page = await browser.newPage()

    await page.setViewport(kwargs["viewport"])

    try:
        yield page
    finally:
        await page.close()


async def install_browser():
    logger.error(
        "请自行安装 chromium 内核的浏览器，例如 Edge、Google Chrome、Chromium、360极速浏览器，并在配置文件中 chromium_path 项指定此浏览器可执行文件的路径"
    )
