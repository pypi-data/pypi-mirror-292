# pysswordSz

[![](https://img.shields.io/badge/version-v0.2.8-blue)](https://github.com/SidneyLYZhang/pysswordSz/releases)

一个使用Python编写的密码管理器，除了可以管理密码之外，还可以作为一个简单的加密软件。
A password manager in Python that not only manages passwords but also serves as a simple encryption software.

为什么不适用现有的那些密码软件？因为奇怪的公司要求使用不了。保存在加密的excel里面，很多时候是有问题的，解密后会被别人看到所有信息，这反而更容易泄密。
所以只好自己来搞一个更安全一些的东西了。Why not use the existing password software? Because strange companies require alternatives. Storing passwords in an encrypted Excel file often poses problems; once decrypted, all information can be seen by others, making it more prone to leaks. Therefore, I have to create a more secure solution myself.

完全使用Python构建的密码管理器和简单加密软件，使用RSA进行加密，密码本保存在本地。这个小程序本身并不支持把密码进行云端同步，如果你确实需要云同步，则需要重新指定你的密码本保存位置，并按照自主设定云同步方案。This Password Manager and simple encryption software completely built with Python, using RSA for encryption, with the password database stored locally. This application does not support cloud synchronization of passwords. If you do require cloud synchronization, you will need to specify a new location for your password database and set up your own synchronization plan.

## 安装 Installation

直接使用Python Pip进行安装：

```bash
$ python -m pip install pysswordsz
```

或者使用`pipx`进行安装：

```bash
$ pipx install pysswordsz
```

如果你使用windows操作系统，也和我的很多同事一样，是个python苦手，那么我推荐使用我打包好的`exe`程序及对应的安装脚本（[`install.ps1`](install.ps1)）进行安装，相关说明见[对应文件](How_to_use_it_for_my_colleagues_zh_cn.md)。安装需要把安装脚本和打包文件放在同一个文件夹下，才能正常完成安装。打包的压缩文件可以在[Releases](https://github.com/SidneyLYZhang/pysswordSz/releases)里面下载。

另外，需要特别注意的是：目前打包的exe程序在创建[xkcd密码](https://xkcd.com/936/)时会出错，这个问题暂时我还未解决，除此之外的功能可以正常使用。如果发现还有什么问题或者有更好的建议欢迎给我[提出建议](https://github.com/SidneyLYZhang/pysswordSz/issues)。

## 快速开始 Quick Start

如果你只使用密码生成的功能，那么，你无需进行任何设置。
但是，如果你需要使用密码库或者进行加密操作，那必须先初始化整体功能：

```bash
$ pysswordsz init
```

如果你需要在其他地方保存key文件和数据文件，你需要在初始化后进行设置：

```bash
$ pysswordsz config set keyfolder '~\place\you\want'
$ pysswordsz config set datafolder '~\place\you\want'
```

但请注意！key文件和数据文件的保存地址需要提前创建好，再进行设置，否则会没有相关路径而使程序出错。

正常加密一个文件和解密一个文件：

```bash
$ pysswordsz crypt encr '.../your.file'
$ pysswordsz crypt decr '.../your.file.lyz'
```

使用密码库，首先需要建立一个库，名称可以是任意的，这里随便起了一个叫做`firstVault`：

```bash
$ pysswordsz pass build 'firstVault'
```

然后就可以添加密码了：

```bash
$ pysswordsz pass add system_one
```

如果你有多个密码库，则添加时需要指定一个你要保存的密码库：

```bash
$ pysswordsz pass add system_two --to oneVault
```

当然，可以通过配置命令指定默认库，不做指定的话，最后新建的密码库就是默认的密码库，下面是指定密码库的操作：

```bash
$ pysswordsz config set vault thatVault
```

当你在默认密码库中保存了多个密码时，当需要查找密码时，可以如下操作：

```bash
$ pysswordsz pass search oneSystem
```

当然，你也可以指定列出某一个系统曾经使用过的所有密码：

```bash
$ pysswordsz pass search twoSystem --all
```

最后一个常用操作，就是更新一个密码：

```bash
$ pysswordsz pass update theSystem
```

## 配置 Configuration

目前支持以下可配置信息：

| name | info | comment |
| --- | --- | --- |
| `keyfolder` | 密钥保存文件夹 |  |
| `datafolder` | 数据保存文件夹 | 包括密码库和加密数据列表 |
| `vault` | 默认密码库 |  |
| `vaultList` | 所有密码库列表 | 使用`;`隔开各密码库名称的字符串信息；可用于导入旧密码库 |
| `columns` | 密码库遵循的关键列名称 | 默认为： |

使用以下命令语法管理配置信息：

```bash
$ pysswordsz config set <name> <value>
$ pysswordsz config rm <name>
```

## 数据导出与加载 Export & Loads

配置文件和密码库是可以迁移的。目前仅支持在当前是空数据时的导入，也就是简单迁移。
暂时还不支持与已有数据进行合并，所以请特别注意这一点。

导入操作：

```bash
$ pysswordsz load
```

导出操作：

```bash
$ pysswordsz export
```

## 依赖信息 Dependency

pysswordSz 的构建主要依赖以下关键Package：

| Package | Version | License |
| --- | --- | --- |
| [pycryptodome](https://www.pycryptodome.org/) | 3.20.0 | BSD 2-Clause license |
| [typer](https://github.com/tiangolo/typer) | 0.12.3 | MIT License |
| [pyperclip](https://github.com/asweigart/pyperclip) | 1.9.0 | BSD-3-Clause license |
| [pyyaml](https://pyyaml.org/) | 6.0.1 | MIT License |
| [polars](https://pola.rs) | 1.3.0 | [LICENSE](https://github.com/pola-rs/polars/blob/main/LICENSE) |

使用[`nuitka`](https://nuitka.net/)完成针对Windows的程序打包。

## 许可信息 License

pysswordSz is licensed under GPL-3.0 license.

pysswordSz  Copyright (C) 2024  Sidney Zhang <zly@lyzhang.me>

This program comes with ABSOLUTELY NO WARRANTY; for details type `show w`.
This is free software, and you are welcome to redistribute it
under certain conditions; type `show c` for details.