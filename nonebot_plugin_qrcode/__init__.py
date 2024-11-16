from io import BytesIO
from typing import List, cast, TypeVar, Callable  # , Optional, Dict, Any

import aiohttp
import nonebot
from nonebot.adapters.onebot.v11 import (
    # GroupMessageEvent,
    Message,
    MessageEvent,
    # PrivateMessageEvent,
    # Bot,
    Event,
)


from nonebot.matcher import Matcher

# from nonebot.params import CommandArg, ShellCommandArgv
# from nonebot.rule import ArgumentParser
# from nonebot.exception import ParserExit
# from nonebot.typing import T_State
# from nonebot.log import logger


nonebot.require("nonebot_plugin_waiter")
from nonebot_plugin_waiter import waiter


from PIL import Image
from pyzbar.pyzbar import decode

# 还是坑，先别导
# from .data_source import generate_qrcode


__version__ = "0.1.0"

# # 说实话，我觉得没啥必要了，这个
# qr_map: Dict[str, str] = {}


# async def check_qrcode(event: MessageEvent, state: T_State) -> bool:
#     if isinstance(event, MessageEvent):
#         for msg in event.message:
#             if msg.type == "image":
#                 url: str = msg.data["url"]
#                 state["url"] = url
#                 return True
#         return False


# notice_qrcode = on_message(check_qrcode, block=False, priority=90)


# @notice_qrcode.handle()
# async def handle_pic(event: MessageEvent, state: T_State):
#     if isinstance(event, GroupMessageEvent):
#         try:
#             group_id: str = str(event.group_id)
#             qr_map.update({group_id: state["url"]})
#         except AttributeError:
#             pass
#     elif isinstance(event, PrivateMessageEvent):
#         try:
#             user_id: str = str(event.user_id)
#             qr_map.update({user_id: state["url"]})
#         except ArithmeticError:
#             pass


# pqr = on_command("pqr", aliases={"前一二维码", "pqrcode"})


# @pqr.handle()
# async def handle_pqr(event: MessageEvent):
#     try:
#         url: str = (
#             qr_map[str(event.group_id)]
#             if isinstance(event, GroupMessageEvent)
#             else qr_map[str(event.user_id)]
#         )

#         async with AsyncClient() as client:
#             res = await client.get(url=url, timeout=10)
#         img = Image.open(BytesIO(res.content))
#         data = decode(img)
#         for i in range(len(data)):
#             qr_data = data[i][0]
#             await pqr.send(str(qr_data.decode()))
#             await sleep(3)
#         await pqr.finish()
#     except IndexError:
#         await pqr.finish()
#     except KeyError:
#         await pqr.finish("图不对！")


command_heads = {
    "scan",
    "scan_qr",
    "scan_qrcode",
    "scan_qr_code",
    "qrcode",
    "qr_code",
    "qr",
    "二维码",
    "扫码",
    "扫二维码",
}
"""
命令头
"""


# 以下授权内容改编或拷贝自 nonebot_plugin_alconna/util.py 及 nonebot_plugin_alconna/matcher.py#800
# Alconna 插件版本 0.46.6
# 遵循 MIT 协议，以下为协议原本
"""MIT License

Copyright (c) 2021 nonebot

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
SOFTWARE."""

# 授权内容开始

TCallable = TypeVar("TCallable", bound=Callable)


def annotation(**types):
    def wrapper(func: TCallable) -> TCallable:
        func.__annotations__ = types
        return func

    return wrapper


async def ask_for_prompt(
    matcher: type[Matcher], message: str | Message, timeout: float = 120
):
    """等待用户输入并返回结果

    参数:
        message: 提示消息
        timeout: 等待超时时间
    返回值:
        符合条件的用户输入
    """
    await matcher.send(message)

    @annotation(event=Event)
    async def wrapper(event: Event):
        return event.get_message()

    wait = waiter(["message"], keep_session=True)(wrapper)
    res = await wait.wait(timeout=timeout)
    if res is None:
        return
    return cast(Message, res)


# 授权内容结束


async def get_url(url: str) -> BytesIO:
    """
    异步下载图片，以字节流返回
    """
    async with aiohttp.ClientSession() as client:
        res = await client.get(url=url, timeout=10)
        return BytesIO(await res.read())


async def pic_deal_and_finish(matcher: type[Matcher], images: List[Image.Image | str]):
    """
    集中处理你码
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


async def check_for_scan(
    event: MessageEvent,
    # state: T_State,
) -> bool:
    """
    检查是否为扫码指令
    """

    # print("检查消息满足扫码要求：", event)
    if isinstance(event, MessageEvent):
        # print("此为原始信息：", event.raw_message)
        # event.message
        for msg in event.message:
            # print("这是其中一个信息---", msg)
            if msg.type == "text" and (msgdata := msg.data["text"].strip()):
                if msgdata in command_heads:
                    # print("判断：这确实是扫码指令发出")
                    return True
                else:
                    # print("判断：这不是扫码的指令")
                    return False
        return False


scan = nonebot.on_message(
    rule=check_for_scan,
    block=False,
    priority=90,
)


@scan.handle()
async def handle_pic(
    event: MessageEvent,
    # state: T_State,
    # arg: Optional[Message] = CommandArg(),
):
    # print("正在解决reply指令……")
    images = []
    if event.reply:
        for msg_sag in event.reply.message:
            if msg_sag.type == "image":
                images.append(Image.open(await get_url(msg_sag.data["url"])))
            # else:
            #     images.append("这啥？")

    # print(arg)
    if event.message:
        for msg in event.message:
            if msg.type == "image":
                images.append(Image.open(await get_url(msg.data["url"])))
            # else:
            #     images.append("这啥？")

    if not images:
        if not (
            pic_promargs := await ask_for_prompt(
                scan,
                "图呢？",
            )
        ):
            await scan.finish("戈闷，妹图郎个解得开嘛？")

        for msg_sag in pic_promargs:
            if msg_sag.type == "image":
                images.append(Image.open(await get_url(msg_sag.data["url"])))
            else:
                images.append("这啥？")

    await pic_deal_and_finish(scan, images)


# qrcode = on_alconna(
#     command=Alconna(
#         "qrcode",
#         Args[
#             "arguments", MultiVar(Any), ()
#         ],  # 这里类型检查给我报 MultiVar 的 Any 的错，但能运行，先留着
#     ),
#     aliases=command_heads,
#     # rule=check_query_for_scan,
#     skip_for_unmatch=False,
#     block=False,
#     priority=90,
#     use_origin=True,
# )

# # @scancode.handle()
# # async def scn(event: MessageEvent, state: T_State):
# #     print("出一个---", event)

# # # 响应消息内容中发送的二维码图片
# # qrcode = nonebot.on_command("qrcode", aliases={"qr", "二维码", "扫码"},)


# # @qrcode.handle()
# async def handle_first_receive(
#     event: MessageEvent,
#     state: T_State,
#     bot: Bot,
#     result: Arparma,
#     # arg: UniMessage = CommandArg(),
# ):

#     # print("这是返回的判定结果", result.main_args.get("arguments", ()))
#     # for i in result.main_args.get("arguments", ()):
#     #     print(type(i), i)
#     print("正在解决qrcode指令……")

#     images: List[Image.Image | str] = [
#         (
#             i
#             if isinstance(i, (Image.Image,))
#             else (
#                 Image.open(await get_url(i.url))
#                 if isinstance(i, (uniseg.Image,))
#                 else f"这啥？"
#             )
#         )
#         for i in result.main_args.get("arguments", ())
#     ]

#     # arg_msg = (
#     #     (arg_msg.extend(event.reply.message) if arg_msg else event.reply.message)
#     #     if event.reply
#     #     else arg_msg
#     # )

#     if not images:
#         if not (
#             pic_promargs := await qrcode.prompt(
#                 "图呢？",
#             )
#         ):
#             await qrcode.finish(UniMessage.text("戈闷，妹图郎个解得开嘛？"))

#         for msg_sag in pic_promargs:
#             if msg_sag.type == "image":
#                 images.append(Image.open(await get_url(msg_sag.data["url"])))
#             else:
#                 images.append("这啥？")

#     await pic_deal_and_finish(qrcode, images)


# @qrcode.got("qr_img", prompt="图呢")
# async def get_qr_img(state: T_State):
#     msg: Message = state["qr_img"]
#     # try:
#     for msg_sag in msg:
#         if msg_sag.type == "image":
#             url = msg_sag.data["url"]

#             async with aiohttp.ClientSession() as client:
#                 res = await client.get(url=url, timeout=10)

#             if data := decode(Image.open(BytesIO(await res.read()))):
#                 await qrcode.finish(
#                     "\n".join([str(piece[0].decode()) for piece in data])
#                 )
#                 # for piece in data:
#                 #     await qrcode.send()
#                 #     await sleep(3)
#             else:
#                 await qrcode.finish("你这也没码啊！")
#         else:
#             # 那这和没有for有啥区别？
#             await qrcode.finish("这啥？指令已取消")


# TODO 生码部分

# parser = ArgumentParser("gqr", description="生成二维码")
# parser.add_argument("-m", "--mask", help="添加图像遮罩", action="store_true")
# parser.add_argument("-e", "--embeded", help="添加中间logo", action="store_true")

# gqr = on_shell_command(
#     "gqr",
#     parser=parser,
#     aliases={"生成二维码", "二维码生成", "gqrcode"},
#     priority=10,
# )


# @gqr.handle()
# async def handle_gqr(argv: List[str] = ShellCommandArgv()):
#     try:
#         args = parser.parse_args(argv)
#     except ParserExit as e:
#         await gqr.finish(e.message)

#     await gqr.finish(f"mask = {args.mask}, embeded = {args.embeded}")
#     # if not arg:
#     #     await gqr.finish(help_message)
