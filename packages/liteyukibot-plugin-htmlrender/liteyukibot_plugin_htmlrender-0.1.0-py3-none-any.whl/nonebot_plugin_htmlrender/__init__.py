import nonebot

from liteyuki.log import logger
from nonebot.plugin import PluginMetadata
from liteyuki.plugin import PluginMetadata as LiteyukiPluginMetadata, PluginType

from .browser import (
    get_browser as get_browser,
    get_new_page as get_new_page,
    shutdown_browser as shutdown_browser,
)
from .data_source import (
    capture_element as capture_element,
    html_to_pic as html_to_pic,
    md_to_pic as md_to_pic,
    template_to_html as template_to_html,
    template_to_pic as template_to_pic,
    text_to_pic as text_to_pic,
)

"""

修改自 nonebot-plugin-htmlrender (MIT LICENSE)

原协议如下：

```
MIT License

Copyright (c) 2021 kexue

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

现协议如下：


版权所有 © 2024 金羿Eilles(EillesWan@outlook.com) & kexue
Copyright (R) 2024 EillesWan(EillesWan@outlook.com) & kexue

轻雪页面渲染重定向组件 的 协议颁发者 是 金羿Eilles(EillesWan@outlook.com)

轻雪页面渲染重定向组件 根据 第一版 汉钰律许可协议（“本协议”）授权。
任何人皆可从以下地址获得本协议副本：[轻雪仓库](https://github.com/LiteyukiStudio/LiteyukiBot/tree/main/src/utils/htmlrender/LICENSE.md)。
若非因法律要求或经过了特殊准许，此作品在根据本协议“原样”提供的基础上，不予提供任何形式的担保、任何明示、任何暗示或类似承诺。也就是说，用户将自行承担因此作品的质量或性能问题而产生的全部风险。
详细的准许和限制条款请见原协议文本。


"""


__liteyuki_plugin_meta__ = LiteyukiPluginMetadata(
    name="轻雪页面渲染重定向组件",
    description="提供跨平台的多用途页面渲染功能，是nontbot-plugin-htmlrender的高级替代",
    usage="提供多个易用API md_to_pic html_to_pic text_to_pic template_to_pic capture_element 等",
    type=PluginType.MODULE,
    author="金羿Eilles",
    homepage="https://github.com/LiteyukiStudio/liteyukibot-plugin-htmlrender",
    extra={
        "license": "汉钰律许可协议 第一版",
    },
)


__plugin_meta__ = PluginMetadata(
    name="nonebot-plugin-htmlrender",
    description="通过浏览器渲染图片",
    usage="提供多个易用API md_to_pic html_to_pic text_to_pic template_to_pic capture_element 等",
    type="library",
    homepage="https://github.com/kexue-z/nonebot-plugin-htmlrender",
    extra={},
)

driver = nonebot.get_driver()


@driver.on_startup
async def init(**kwargs):
    """Start Browser

    Returns:
        Browser: Browser
    """
    browser = await get_browser(**kwargs)
    logger.info("浏览器，启动！")
    return browser


@driver.on_shutdown
async def shutdown():
    await shutdown_browser()
    logger.info("浏览器关停。")


browser_init = init

__all__ = [
    "browser_init",
    "capture_element",
    "get_new_page",
    "html_to_pic",
    "md_to_pic",
    "template_to_html",
    "template_to_pic",
    "text_to_pic",
]
