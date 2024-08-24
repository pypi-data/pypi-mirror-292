import os
import uuid
from os import getcwd
from typing import Any, Dict, Literal, Optional, Union

from liteyuki.log import logger

from src.utils.htmlrender import (
    TEMPLATES_PATH,
    env,
    text_to_pic as txt2pic,
    md_to_pic as md2pic,
    read_any,
    template_to_html,
    html_to_pic as html2pic,
    write_any,
    template_to_pic as tpl2pic,
)

from .browser import get_new_page


async def text_to_pic(
    text: str,
    css_path: str = "",
    width: int = 500,
    type: Literal["jpeg", "png"] = "png",  # noqa: A002
    quality: Union[int, None] = None,
    device_scale_factor: float = 2,
) -> bytes:
    """多行文本转图片

    Args:
        text (str): 纯文本, 可多行
        css_path (str, optional): css文件
        width (int, optional): 图片宽度，默认为 500
        type (Literal["jpeg", "png"]): 图片类型, 默认 png
        quality (int, optional): 图片质量 0-100 当为`png`时无效
        device_scale_factor: 缩放比例,类型为float,值越大越清晰(真正想让图片清晰更优先请调整此选项)

    Returns:
        bytes: 图片, 可直接发送
    """

    return await txt2pic(
        text=text,
        css_path=css_path,
        width=width,
        type_=type,
        quality=quality,
        device_scale_factor=device_scale_factor,
    )


async def md_to_pic(
    md: str = "",
    md_path: str = "",
    css_path: str = "",
    width: int = 500,
    type: Literal["jpeg", "png"] = "png",  # noqa: A002
    quality: Union[int, None] = None,
    device_scale_factor: float = 2,
) -> bytes:
    """markdown 转 图片

    Args:
        md (str, optional): markdown 格式文本
        md_path (str, optional): markdown 文件路径
        css_path (str,  optional): css文件路径. Defaults to None.
        width (int, optional): 图片宽度，默认为 500
        type (Literal["jpeg", "png"]): 图片类型, 默认 png
        quality (int, optional): 图片质量 0-100 当为`png`时无效
        device_scale_factor: 缩放比例,类型为float,值越大越清晰(真正想让图片清晰更优先请调整此选项)

    Returns:
        bytes: 图片, 可直接发送
    """

    return await md2pic(
        md=md,
        md_path=md_path,
        css_path=css_path,
        width=width,
        type_=type,
        quality=quality,
        device_scale_factor=device_scale_factor,
    )


async def read_file(path: str) -> str:
    return await read_any(path, "r")  # type: ignore


async def read_tpl(path: str) -> str:
    return await read_file(f"{TEMPLATES_PATH}/{path}")


async def html_to_pic(
    html: str,
    wait: int = 0,
    template_path: str = f"file://{getcwd()}",  # noqa: PTH109
    type: Literal["jpeg", "png"] = "png",  # noqa: A002
    quality: Union[int, None] = None,
    device_scale_factor: float = 2,
    **kwargs,
) -> bytes:
    """html转图片

    Args:
        html (str): html文本
        wait (int, optional): 等待时间. Defaults to 0.
        template_path (str, optional): 模板路径 如 "file:///path/to/template/"
        type (Literal["jpeg", "png"]): 图片类型, 默认 png
        quality (int, optional): 图片质量 0-100 当为`png`时无效
        device_scale_factor: 缩放比例,类型为float,值越大越清晰(真正想让图片清晰更优先请调整此选项)
        **kwargs: 传入 page 的参数

    Returns:
        bytes: 图片, 可直接发送
    """

    await write_any(
        html_path_ := os.path.join(template_path, "{}.html".format(uuid.uuid4())),
        html,
    )

    if device_scale_factor:
        if "viewport" not in kwargs:
            kwargs["viewport"] = {
                "deviceScaleFactor": device_scale_factor,
            }
        else:
            kwargs["viewport"]["deviceScaleFactor"] = device_scale_factor

    img_ = await html2pic(
        html_path=html_path_,
        wait=wait,
        type_=type,
        quality=quality,
        viewport=kwargs.get("viewport", {}),
        cookie=kwargs.get("cookie", {}),
        user_agent=kwargs.get("user_agent", ""),
    )

    os.remove(html_path_)

    return img_


async def template_to_pic(
    template_path: str,
    template_name: str,
    templates: Dict[Any, Any],
    pages: Optional[Dict[Any, Any]] = None,
    wait: int = 0,
    type: Literal["jpeg", "png"] = "png",  # noqa: A002
    quality: Union[int, None] = None,
    device_scale_factor: float = 2,
) -> bytes:
    """使用jinja2模板引擎通过html生成图片

    Args:
        template_path (str): 模板路径
        template_name (str): 模板名
        templates (Dict[Any, Any]): 模板内参数 如: {"name": "abc"}
        pages (Optional[Dict[Any, Any]]): 网页参数 Defaults to
            {"base_url": f"file://{getcwd()}", "viewport": {"width": 500, "height": 10}}
        wait (int, optional): 网页载入等待时间. Defaults to 0.
        type (Literal["jpeg", "png"]): 图片类型, 默认 png
        quality (int, optional): 图片质量 0-100 当为`png`时无效
        device_scale_factor: 缩放比例,类型为float,值越大越清晰(真正想让图片清晰更优先请调整此选项)
    Returns:
        bytes: 图片 可直接发送
    """

    return await tpl2pic(
        template_path=template_path,
        template_name=template_name,
        templates=templates,
        pages=pages,
        wait=wait,
        type_=type,
        quality=quality,
        device_scale_factor=device_scale_factor,
    )


async def capture_element(
    url: str,
    element: str,
    timeout: float = 0,
    type: Literal["jpeg", "png"] = "png",  # noqa: A002
    quality: Union[int, None] = None,
    **kwargs,
) -> bytes:
    async with get_new_page(**kwargs) as page:
        page.on("console", lambda msg: logger.debug(f"浏览器控制台: {msg.text}"))
        await page.goto(url, timeout=timeout)
        await page.select(element)
        await page.focus(element)
        return await page.screenshot(
            type=type,
            quality=quality,
        )  # type: ignore
