# nonebot-plugin-qrcode

- 本地识别二维码
- 支持一图片多个二维码
- 支持多图片(>=0.1.0)
- 支持回复图片进行识别(>=0.1.0)

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

- `qr`

  - 如果指令后**有图片**，则直接识别图片
  - 如果**没有图片**，则会询问图片
  - 如果在指令的回复中含有图片，则会识别回复内容
<!-- 
- `pqr`
  - 识别聊天中，上一条图片消息中的二维码
  - 仅版本 <= 0.0.6
-->

# 挖坑

- [ ] 文本转二维码

# 有疑问

- ~~自己想~~
- pr 或 issue
