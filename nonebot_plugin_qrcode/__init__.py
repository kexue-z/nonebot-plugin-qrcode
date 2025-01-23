from typing import List, cast, Any

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
from nonebot.log import logger


nonebot.require("nonebot_plugin_waiter")
from nonebot_plugin_waiter import waiter  # noqa: E402

nonebot.require("nonebot_plugin_alconna")

from nonebot_plugin_alconna.util import annotation  # noqa: E402
from nonebot_plugin_alconna import (  # noqa: E402
    AlconnaMatcher,
    on_alconna,
    Alconna,
    Option,
    Args,
    MultiVar,
    Arparma,
    store_true,
    Image as Alconna_Image,
    UniMessage,
)

from PIL import Image  # noqa: E402

from .data_source import generate_qrcode, pic_deal_and_finish, get_url  # noqa: E402


__version__ = "0.2.0"

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
    "scanqr",
    "二维码",
    "扫码",
    "扫二维码",
    "识别你码",
    "识别此码",
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
async def ask_for_prompt(
    matcher: type[Matcher | AlconnaMatcher],
    message: str | Message,
    timeout: float = 120,
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
                # print("============", msg_sag.data.get("url"))
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


generateqr = on_alconna(
    command=Alconna(
        "gqr",
        Args[
            "data",
            MultiVar(
                Any  # type:ignore  这里类型检查给我报 MultiVar 的 Any 的错，但能运行，先留着
            ),
            None,
            # Field(completion=lambda: "请给出码的内容"),
        ],
        Option(
            name="-m|--mask",
            args=Args[
                "mask_image?",
                MultiVar(Alconna_Image),
                (),
            ],
            default=False,
            help_text="添加图像色彩遮罩",
            action=store_true,
        ),
        Option(
            name="-e|--embeded",
            args=Args[
                "embeded_image?",
                MultiVar(Alconna_Image),
                (),
            ],
            default=False,
            help_text="添加中心嵌入图",
            action=store_true,
        ),
        # Args[
        #     "addition", MultiVar(Any), ()
        # ],
    ),
    aliases={"生成二维码", "二维码生成", "gqrcode", "generate-qrcode", "生码"},
    priority=10,
)


# parser = ArgumentParser("gqr", description="生成二维码")
# parser.add_argument("data", help="二维码数据", action="store")
# parser.add_argument("-m", "--mask", help="添加图像色彩遮罩", action="store")
# parser.add_argument("-e", "--embeded", help="添加中心嵌入图", action="store")


# gqr = nonebot.on_shell_command(
#     "gqr",
#     parser=parser,
#     aliases={"生成二维码", "二维码生成", "gqrcode", "generate-qrcode", "生码"},
#     priority=10,
# )


def _getdata(x):
    return " ".join(
        [
            (
                msg_sag
                if isinstance(
                    msg_sag,
                    (str,),
                )
                else (
                    (msg_sag.data["url"])
                    if "url" in msg_sag.data
                    else (
                        msg_sag.data["text"] if "text" in msg_sag.data else str(msg_sag)
                    )
                )
            )
            for msg_sag in x
        ]
    )


@generateqr.handle()
async def handle_gqr(
    result: Arparma,
    event: MessageEvent,
    # bot: Bot,
):
    # try:
    #     args = parser.parse_args(argv)
    # except ParserExit as e:
    #     await gqr.finish(e.message)

    # WARNING
    # 以下注意仅适用于 Windows 环境
    # 当 nonebot-plugin-alconna 版本与 0.46.3 兼容、时（具体到哪个版本忘了）
    # arclet_alconna==1.8.15 且 arclet_alconna_tools==0.7.6 时
    # result 中 Option 后有参数时，其 Value 为 None
    # 在这个版本之后，当 Option 后有参数时，其 value 为 Ellipsis
    # 但是因为我设置了默认为 False 所以在没参数的时候必定为 False
    # 在我以上提到的这个版本下，Alconna在如果没有后面的参数的情况下就不会在 args 里面有这个Key
    # 所以！！
    # 在 Linux 环境，或者在这个版本之后
    # 在 Args 里面无论如何都有这个 Key，如果在没指定参数的时候就是默认参数
    # 也就是之前的 [i for j in result.other_args.values() for i in j] 会解包到 false
    # 于是报错

    # logger.info(f"{event.user_id} 尝试生成二维码：")
    # logger.info(result.other_args)
    # logger.info([j for j in result.other_args.values()]) # False False

    passed_images: List[Image.Image] = [
        Image.open(await get_url(msg_sag.data["url"]))
        for msg_sag in [
            i for j in result.other_args.values() if j is not False for i in j
        ]
        if msg_sag.type == "image"
    ]

    args_to_pass = dict(
        zip(
            [i[0] for i in result.other_args.items() if i[1] is not False],
            passed_images,
        )
    )

    if len(passed_images) > len(args_to_pass):
        await generateqr.finish(
            UniMessage.text("你给这么多图干嘛，这哪跟哪啊！？指令已取消。")
        )
    elif len(passed_images) < len(args_to_pass):
        await generateqr.finish(UniMessage.text("你少图了，指令已取消。"))

    # print("读入参数：", result.main_args)
    # print("其他参数：", result.other_args)
    # print("读入选项：", result.options)

    final_data = None

    # 挑战不可能尝试失败
    # if event.reply:
    #     print("这是回复数据", event.reply.message)

    if "data" in result.main_args:
        final_data = _getdata(result.main_args["data"])

    if not final_data:
        if not (
            data_promargs := await ask_for_prompt(
                generateqr, "请给出要生成的二维码数据"
            )
        ):
            await scan.finish("这啥啊，空数据？")

        if data_promargs.has("reply"):
            start_for = data_promargs.index("reply") + 1
        else:
            start_for = 0

        final_data = _getdata(data_promargs[start_for:])

        # for msg_sag in data_promargs[start_for:]:
        #     msg_sag.data

    # print(
    #     "输入的参数：{}".format(args_to_pass),
    # )

    try:
        await generateqr.finish(
            UniMessage.image(raw=generate_qrcode(final_data, **args_to_pass))  # type: ignore 这里 args 肯定是不满足类型检查的，不信去掉 type ignore 试试
        )
    except TypeError as e:
        await generateqr.finish(
            UniMessage.text(
                "！生成二维码时发生错误，你可能使用了动态图片作为遮罩。\n" + str(e)
            )
        )

    # if not arg:
    #     await gqr.finish(help_message)
