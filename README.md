# nonebot-plugin-qrcode

- 本地识别二维码
- 支持一图片多个二维码
- 支持多图片(>=0.1.0)
- 支持回复图片进行识别(>=0.1.0)
- 支持带遮罩与内嵌图生成二维码(>=0.2.0)

# 下载&安装

## 插件本体

```bash
pip install -U nonebot-plugin-qrcode
```

## !!!必须要的库 `libzbar0`

> 此操作仅在非 Windows 环境下需要进行

### docker / ubuntu 等使用 `apt` 的

```
apt install -y libzbar0
```

### centos

```
dnf install -y zbar/yum install -zbar
```

## **在部分 Windows 设备下可能出现的问题**

> 此操作仅在 Windows NT 环境下需要进行

当你真的在使用 Windows Server 作为机器人运行环境的时候，你可能真的不怎么会在意一些常用支持库的安装。\
因此，特别是在一些需要蛮多系统支持库的库的运行时，会出现报错；比如出现如下情况：

```
FileNotFoundError: Could not find module '.\[Python包目录]\pyzbar\libzbar-64.dll' (or one of its dependencies). Try using the full path with constructor syntax.
```

这很可能是由于 msvcr 库没有正常安装导致的。请前往 [微软 Visual C++ Redistributable Packages for Visual Studio 2013 下载页](https://www.microsoft.com/zh-cn/download/details.aspx?id=40784) 下载对应你系统的版本。

# 使用

以下默认你设置了 `COMMAND_START=""`

- `scan` | `扫码`

  扫描一个码，支持多种码。什么种类？试试就知道了。

  - 如果指令后**有图片**，则直接识别图片
  - 如果**没有图片**，则会询问图片
  - 如果在指令的回复中含有图片，则会识别回复内容

- `gqr` | `生成二维码`

  生成二维码，支持图片转链接地址，支持自定义遮罩图片和中央嵌入图片。

  - 指令后的内容为二维码内容。其中图片会转为链接。
  - `-e|--embeded` 开关控制是否在二维码中心嵌入图片
  - `-m|--mark` 开关控制是否增加遮罩图片
  
  注意：\
  考虑到部分手机用户无法通过全屏输入的方式在文字中穿插图片，所以当启用 -e 或 -m 开关时，可以在消息末尾提交图片；如果直接穿插在开关后面也是没问题的。但是，如果图片数量与开启的选项开关的数量不符，则会停止生成。当使用 GIF 图像作为内嵌的图片（-e）时，二维码生成会失败。\
  如果在开关之后混入了其他不是图像消息的内容，也会视作二维码内容的一部分，生成进二维码中。\
  当你只发起指令而不给任何内容时，机器会好心问你讨要二维码内容；但是如果你是在指令后面带了选项开关还不给内容时，机器也不会理你的。

- `pqr` （已弃用）
  - 识别聊天中，上一条图片消息中的二维码
  - 仅版本 <= 0.0.6


# 有疑问

- ~~自己想~~
- pr 或 issue
