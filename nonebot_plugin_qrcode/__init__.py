from asyncio import sleep
from io import BytesIO
from typing import Dict, List

from httpx import AsyncClient
from nonebot import on_command, on_message, on_shell_command
from nonebot.adapters.onebot.v11 import (
    GroupMessageEvent,
    Message,
    MessageEvent,
    PrivateMessageEvent,
)
from nonebot.params import CommandArg, ShellCommandArgv
from nonebot.rule import ArgumentParser, ParserExit
from nonebot.typing import T_State
from PIL import Image
from pyzbar.pyzbar import decode

from .data_source import generate_qrcode

qr_map: Dict[str, str] = {}

async def check_qrcode(event: MessageEvent, state: T_State) -> bool:
    if isinstance(event, MessageEvent):
        for msg in event.message:
            if msg.type == "image":
                url: str = msg.data["url"]
                state["url"] = url
                return True
        return False


notice_qrcode = on_message(check_qrcode, block=False, priority=90)


@notice_qrcode.handle()
async def handle_pic(event: MessageEvent, state: T_State):
    if isinstance(event, GroupMessageEvent):
        try:
            group_id: str = str(event.group_id)
            qr_map.update({group_id: state["url"]})
        except AttributeError:
            pass
    elif isinstance(event, PrivateMessageEvent):
        try:
            user_id: str = str(event.user_id)
            qr_map.update({user_id: state["url"]})
        except ArithmeticError:
            pass


pqr = on_command("pqr", aliases={"前一二维码", "pqrcode"})


@pqr.handle()
async def handle_pqr(event: MessageEvent):
    try:
        url: str = (
            qr_map[str(event.group_id)]
            if isinstance(event, GroupMessageEvent)
            else qr_map[str(event.user_id)]
        )

        async with AsyncClient() as client:
            res = await client.get(url=url, timeout=10)
        img = Image.open(BytesIO(res.content))
        data = decode(img)
        for i in range(len(data)):
            qr_data = data[i][0]
            await pqr.send(str(qr_data.decode()))
            await sleep(3)
        await pqr.finish()
    except (IndexError):
        await pqr.finish()
    except KeyError:
        await pqr.finish("图不对！")


qrcode = on_command("qrcode", aliases={"qr", "二维码"})


@qrcode.handle()
async def handle_first_receive(state: T_State, arg: Message = CommandArg()):
    msg = arg
    if msg:
        state["qr_img"] = msg
    pass


@qrcode.got("qr_img", prompt="图呢")
async def get_qr_img(state: T_State):
    msg: Message = state["qr_img"]
    # try:
    for msg_sag in msg:
        if msg_sag.type == "image":
            url = msg_sag.data["url"]

            async with AsyncClient() as client:
                res = await client.get(url=url, timeout=10)
            img = Image.open(BytesIO(res.content))
            data = decode(img)
            for i in range(len(data)):
                qr_data = data[i][0]
                await qrcode.send(str(qr_data.decode()))
                await sleep(3)
            await qrcode.finish()
        else:
            await qrcode.finish("这啥？指令已取消")


parser = ArgumentParser("gqr", description="生成二维码")
parser.add_argument("-m", "--mask", help="添加图像遮罩", action="store_true")
parser.add_argument("-e", "--embeded", help="添加中间logo", action="store_true")

gqr = on_shell_command(
    "gqr",
    parser=parser,
    aliases={"生成二维码", "二维码生成", "gqrcode"},
    priority=10,
)


@gqr.handle()
async def handle_gqr(argv: List[str] = ShellCommandArgv()):
    try:
        args = parser.parse_args(argv)
    except ParserExit as e:
        await gqr.finish(e.message)

    await gqr.finish(f"mask = {args.mask}, embeded = {args.embeded}")
    # if not arg:
    #     await gqr.finish(help_message)
