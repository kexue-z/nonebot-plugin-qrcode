# nonebot-plugin-qrcode

- 本地识别二维码
- 支持一图片多个二维码
- 支持多图片

# 下载&安装

## 插件本体

```bash
pip install -U nonebot-plugin-qrcode
```

## !!!必须要的库 `libzbar0`

### docker / ubuntu 等使用 `apt` 的

```
apt install -y libzbar0
```

### centos

```
dnf install -y zbar/yum install -zbar
```

# 使用

以下默认你设置了 `COMMAND_START=""`

- `qr`

  - 如果指令后**有图片**，则直接识别图片
  - 如果**没有图片**，则会询问图片

- `pqr`
  - 识别聊天中，上一条图片消息中的二维码

# 挖坑

- [ ] 文本转二维码

# 有疑问

- ~~自己想~~
- pr 或 issue
