from io import BytesIO
from typing import Optional, List

import qrcode
import qrcode.image.styles.moduledrawers.pil

from nonebot.matcher import Matcher

from PIL import Image
from httpx import AsyncClient
from pyzbar.pyzbar import decode
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.colormasks import ImageColorMask

from nonebot_plugin_alconna import AlconnaMatcher

_headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:134.0) Gecko/20100101 Firefox/134.0"
}


# print("这是可用的 Drawers __DICT__:\n\t", qrcode.image.styles.moduledrawers.pil.__dict__)

# try:
#     print("这是可用的 Drawers__ALL__:\n\t", qrcode.image.styles.moduledrawers.pil.__all__)
# except:
#     print("你没有可用的 Drawers")


def generate_qrcode(
    data: str,
    embeded_image: Optional[Image.Image] = None,
    mask_image: Optional[Image.Image] = None,
    module_drawer: Optional[str] = None,
) -> bytes:
    """
    生成二维码

    参数
    ====
        data: str
            二维码数据
        embeded_image: Optional[bytes]
            嵌入的图片
        mask_image: Optional[bytes]
            遮罩图片

    返回值
    =====
        bytes
            二维码图片
    """

    qr = qrcode.QRCode(
        error_correction=qrcode.ERROR_CORRECT_H,
        box_size=10,
        border=1,
        image_factory=StyledPilImage if (embeded_image or mask_image) else None,
    )
    qr.add_data(data)

    if mask_image:
        img = qr.make_image(
            module_drawer=(
                qrcode.image.styles.moduledrawers.pil.__dict__.get(module_drawer, None)
                if module_drawer
                else None
            ),  # 没用的
            embeded_image=embeded_image,
            color_mask=(
                ImageColorMask(color_mask_image=mask_image)
            ),  # 如果是 GIF 则报错；如果是 None 也tm报错；这什么破库
        )
    else:
        img = qr.make_image(
            module_drawer=(
                qrcode.image.styles.moduledrawers.pil.__dict__.get(module_drawer, None)
                if module_drawer
                else None
            ),
            embeded_image=embeded_image,
        )

    result_stream = BytesIO()
    img.save(result_stream, "PNG")
    return result_stream.getvalue()


async def get_url(url: str) -> BytesIO:
    """
    异步下载图片，以字节流返回

    参数
    ====
        url: str
            图片地址

    返回值
    =====
        BytesIO
            图片字节流
    """
    async with AsyncClient(verify=False, timeout=10, headers=_headers) as client: # 他妈的报错啊
        res = await client.get(url=url.replace("https://", "http://"), timeout=10, headers=_headers)
        return BytesIO(res.content)


async def pic_deal_and_finish(
    matcher: type[Matcher | AlconnaMatcher], images: List[Image.Image | str]
):
    """
    集中处理你码

    参数
    ====
        matcher: type[Matcher]
            NoneBot Matcher 对象

    返回值
    =====
        None

    """
    results: List[str] = []

    for img in images:
        if isinstance(img, str):
            results.append(img)
        else:
            if data := decode(img):
                results.append("\n".join([str(piece[0].decode()) for piece in data]))
                # for piece in data:
                #     await qrcode.send()
                #     await sleep(3)
            else:
                results.append("你图没码")

    await matcher.finish("\n\n".join(results))
