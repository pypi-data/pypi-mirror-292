import typer
import pyperclip as clip
import polars as pl

from typing_extensions import Annotated
from pysswordsz.encrytool import generatePassword,newKeys,encryting,generateXKCDPassword
from pysswordsz.pzsconfig import (
    newConfig,
    pszconfig,
    loadConfig,
    exportConfig
)
from rich import print
from pysswordsz.pwsmanager import pwsmanager,buildPWDB

app = typer.Typer(no_args_is_help=True)

config = typer.Typer()
app.add_typer(config, name="config", help="manage config \t\t 管理配置")
passdb = typer.Typer()
app.add_typer(passdb, name="pass", help="manage password \t 管理密码")
cryptl = typer.Typer()
app.add_typer(cryptl, name="crypt", help="encrypt or decrypt \t 加密解密")

@app.command("version", help="show version \t\t 显示版本")
def version():
    print("VERSION 0.2.8")
    print("pysswordSz Copyright (C) 2024  Sidney Zhang <zly@lyzhang.me>")
    print("Licensed under GPL-3.0 license.")

@app.command("load", help="Loading the Core files \t 快速加载已有密码库")
def loading_config():
    loadConfig()

@app.command("export", help="Export all data files \t 导出关键数据")
def exporting():
    exportConfig()

@app.command("gen",help="generate password \t 生成密码")
def genpass(n:Annotated[int,typer.Argument(help="密码位数，建议普通密码至少10位，xkcd密码至少8词",show_default=False)] = 16,
            xkcd:Annotated[bool,typer.Option(help="生成XKCD密码")] = False,
            need_upper:Annotated[bool,typer.Option(help="需要大写字母")] = True,
            need_number:Annotated[bool,typer.Option(help="需要数字")] = True,
            need_punctuation:Annotated[bool,typer.Option(help="需要序号")] = True,
            minia:Annotated[int,typer.Option(help="各类字符的最小个数")] = 1,
            urlsafe:Annotated[bool,typer.Option(help="是否生成链接安全密码")] = False,
            xk_mode:Annotated[str,typer.Option(help="xkcd密码生成模式")] = "pinyin",
            xk_padding:Annotated[bool,typer.Option(help="xkcd密码中是否使用随机填充")] = False,
            show:Annotated[bool,typer.Option(help="是否展示密码")] = True,
            to_clip:Annotated[bool,typer.Option(help="是否复制到系统粘贴板")] = False):
    if xkcd :
        pswds = generateXKCDPassword(n=n, type_mode=xk_mode,
                                     padding=xk_padding)
    else:
        pswds = generatePassword(n = n, need_punctuation=need_punctuation,
                                 need_number=need_number,need_upper=need_upper,
                                 mina=minia, urlsafe=urlsafe)
    if show :
        print(pswds)
    if to_clip :
        clip.copy(pswds)

@app.command(help="init pysswordSz \t 初始化pysswordSz")
def init():
    newConfig()
    newKeys()
    print("The initialization of pysswordSz is complete!")

@config.command("list", help="list all configs / 列出所有已有配置")
def cfg_list():
    data = pszconfig().list()
    print(data)

@config.command("rm", help="remove one of config / 删除一个配置")
def cfg_remove(name:Annotated[str,typer.Argument(help="需要移除的配置名")]):
    pszconfig().remove(name=name)


@config.command("set", help="set one of config / 设置一个配置")
def cfg_setting(name:Annotated[str,typer.Argument(help="需要添加的配置名")],
                value:Annotated[str,typer.Argument(help="配置值")]):
    pszconfig().setting(name=name,value=value)

@passdb.command("build",help="build a vault / 建立密码库")
def pss_build(name:Annotated[str,typer.Argument(help="需要建立的密码库名称")]):
    buildPWDB(name=name)

@passdb.command("add", help="add a password to vault / 向密码库添加密码")
def pss_add(name:Annotated[str,typer.Argument(help="需要添加的密码名称")],
            to:Annotated[str,typer.Option(help="需要添加密码的密码库，默认为最后创建的库",show_default=False)]="default"):
    pwsmanager().add_password(name = name, to = to)

@passdb.command("search",help="search a password in vault / 在密码库中搜索密码")
def pss_search(name:Annotated[str,typer.Argument(help="要查找的密码名称")], 
               last_more:Annotated[int,typer.Option(help="展示旧密码，-1将展示全部，0为不展示，其他正整数为展示长度。")] = 0, 
               vault:Annotated[str,typer.Option(help="需要查找的密码库",show_default=False)]="default",
               show:Annotated[bool,typer.Option(help="是否展示密码")] = False, 
               to_clip:Annotated[bool,typer.Option(help="是否把最新的密码复制到系统粘贴板")] = True):
    mgr = pwsmanager()
    need_all = False if last_more == 0 else True
    data = mgr.search(name = name, all=need_all, vault=vault)
    if data.is_empty():
        print("")
    else:
        if need_all :
            with pl.Config(tbl_rows=-1):
                hl = last_more if last_more>0 else data.height
                needPWS = data.head(hl).select(pl.col("uuid","password","createtime"))
                dddd = needPWS["password"].to_numpy()[0]
                if show:
                    print(needPWS)
                else:
                    print(needPWS.filter(pl.col("password")!=dddd))
                if to_clip:
                    clip.copy(dddd)
        else:
            keyname = data.columns
            for i in keyname:
                if i !="password":
                    print("{} :\t{}".format(i,data[i][0]))
                else:
                    if show :
                        print("{} :\t{}".format(i,data[i][0]))
                    if to_clip :
                        clip.copy(data[i][0])

@passdb.command("update", help="update a password in vault / 更新密码库中的密码")
def pss_update(name:Annotated[str,typer.Argument(help="要更新的密码名称")], 
               vault:Annotated[str,typer.Option(help="指定密码库",show_default=False)]="default"):
    pwsmanager().update(name=name, vault=vault)

@passdb.command("delete",help="delete a password in vault / 删除密码库中的密码")
def pss_delete(name:Annotated[str,typer.Argument(help="要删除的密码名称")], 
               vault:Annotated[str,typer.Option(help="指定密码库",show_default=False)]="default"):
    pwsmanager().delete(name=name, vault=vault)

@passdb.command("list", help="list all passwords in vault / 列出密码库中的所有密码")
def pss_list(vault:Annotated[str,typer.Argument(help="指定所需密码库",show_default=False)]="default", 
             add_columns:Annotated[str,typer.Argument(help="增加需要展示的列名，使用`,`隔开。",show_default=False)] = ""):
    addcolumns = add_columns.split(",") if add_columns else None
    showall = typer.confirm("是否显示所有信息? --> ")
    needrows = -1 if showall else 16
    data = pwsmanager().list(vault=vault, other_columns=addcolumns)
    if data.is_empty():
        print("[green]There is currently no password in Vault {}...".format(vault))
    else :
        with pl.Config(tbl_rows=needrows):
            print(data)

@cryptl.command("encr",help="encrypt a file / 加密一个文件或文件夹")
def ctl_encr(file: Annotated[str, typer.Argument(help="需要加密的文件或文件夹路径")]):
    cipher = encryting()
    cipher.encrypt_file(file)
    print("[green]Encryption is complete!")

@cryptl.command("decr",help="decrypt a file / 解密一个文件或文件夹")
def ctl_decr(file: Annotated[str, typer.Argument(help="需要解密的文件路径")]):
    cipher = encryting()
    cipher.decrypt_file(file)
    print("[green]Decryption is complete!")

@cryptl.command("list",help="list all files / 列出所有加密文件")
def ctl_list():
    dataList = encryting().list_files()
    if dataList.is_empty():
        print("There is currently no encrypted data...")
    else:
        with pl.Config(tbl_rows=-1):
            print(dataList)

def entry_point() -> None:
    app()

def main() -> None:
    entry_point()

if __name__ == "__main__":
    entry_point()