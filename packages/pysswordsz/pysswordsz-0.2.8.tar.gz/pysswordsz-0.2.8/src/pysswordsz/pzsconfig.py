from pathlib import Path
from collections.abc import Callable
import typer
import yaml
import platform
import shutil
import os

def belongto(oripart:Callable, target:Callable) -> bool:
    for i in oripart :
        if i in target :
            return True
    return False

def setting_config():
    # 处理配置位置
    overpath = os.getenv("PYSSWORDSZ")
    if overpath is None :
        if platform.system() == "Windows" :
            overpath = "AppData/Local/pysswordsz"
        else :
            overpath = ".config/pysswordsz"
        conPath = Path.home() / overpath
    else :
        conPath = overpath
    return conPath

def newConfig() -> None:
    data = {
        "columns": ["url","user","comment"],
        "keyfolder":setting_config(),
        "datafolder":setting_config()
    }
    changefolder = typer.confirm("是否更改密钥KEY文件的保存位置?\nDo you want to change the KEY file location?\n--> ")
    if changefolder :
        data["keyfolder"] = typer.prompt("请输入密钥KEY文件的保存位置\nPlease input the KEY file location\n--> ")
    changefolder = typer.confirm("是否更改数据DATA文件的保存位置?\nDo you want to change the DATA file location?\n--> ")
    if changefolder :
        data["datafolder"] = typer.prompt("请输入数据DATA文件的保存位置\nPlease input the DATA file location\n--> ")
    os.mkdir(setting_config())
    with open(setting_config() / "config.yaml", "w", encoding="utf-8") as fx :
        yaml.dump(data, fx)

def loadConfig() -> None:
    if os.getenv("PYSSWORDSZ") is None :
        os.mkdir(setting_config())
        configfolder = Path(
            typer.prompt("请输入配置文件保存位置\nPlease enter the config-file saved location\n--> ")
        )
        shutil.copy(configfolder/"config.yaml", setting_config()/"config.yaml")
        os.remove(configfolder/"config.yaml")
    configData = pszconfig()
    tpath = typer.prompt("请输入密钥KEY文件的保存位置\nPlease input the KEY file location\n--> ")
    configData.setting("keyfolder", tpath)
    tpath = typer.prompt("请输入数据DATA文件的保存位置\nPlease input the DATA file location\n--> ")
    configData.setting("datafolder", tpath)
    print("Complete setting config!")

_EXPORTNOTE_ = """# README

需要特别注意：**加密数据记录不会进行迁移。**

可通过设定`PYSSWORDSZ`的环境变量，来直接导入配置文件，但是需要再确认KEY文件和密码库的保存位置。

文件说明：

- 配置文件的保存位置： `{}`
- 密钥KEY文件的保存位置： `{}`
- 密码DATA文件的保存位置： `{}`
"""

def exportConfig() -> None:
    outputFolder = Path(
        typer.prompt("请输入导出位置\nPlease input the export location\n--> ")
    )
    oriPath = setting_config()
    oriConfig = pszconfig()
    shutil.copytree(oriPath, outputFolder/"configuration")
    shutil.copytree(oriConfig.keyfolder(), outputFolder/"key")
    shutil.copytree(oriConfig.datafolder(), outputFolder/"data")
    os.remove(outputFolder/"encinfoDB.lyz")
    with open(outputFolder/"README.md", "w", encoding="utf-8") as f:
        f.write(_EXPORTNOTE_.format(
            str(outputFolder/"configuration"),
            str(outputFolder/"key"),
            str(outputFolder/"data")
        ))
    print("Complete exported all data!")

class pszconfig(object):
    def __init__(self) -> None:
        self.__home = setting_config() / "config.yaml"
        with open(self.__home, "r", encoding="utf-8") as ftxt:
            self.__data = yaml.load(ftxt.read(),Loader=yaml.FullLoader)
    def __saveconfig(self) -> None :
        with open(self.__home, "w", encoding="utf-8") as fx :
            yaml.dump(self.__data, fx)
    def keyfolder(self) -> Path:
        fp = self.__data["keyfolder"]
        return Path(fp)
    def datafolder(self) -> Path:
        fp = self.__data["datafolder"]
        return Path(fp)
    @property
    def columns(self) -> list:
        return self.__data["columns"]
    @property
    def vaultlist(self) -> list:
        if "vaultlist" in self.__data.keys():
            return self.__data["vaultlist"]
        else :
            return []
    @property
    def vault(self) -> str:
        if "vault" in self.__data.keys():
            return self.__data["vault"]
        else :
            raise ValueError("No vault is set!")
    def list(self) -> None:
        print(self.__data)
    def setting(self, name:str, value:str) -> None:
        if name == "columns":
            if "," in value :
                newcols = value.spilt(",")
            else:
                newcols = list(set(self.columns.append(value)))
            if belongto(newcols,["uuid","name","password","createtime"]) :
                raise KeyError('"uuid" "name" "password" and "createtime" are reserved names.')
            else:
                self.__data[name] = newcols
        else:
            self.__data[name] = value
        self.__saveconfig()
        print("Complete the configuration settings!")
    def remove(self, name:str) :
        if name not in self.__data.keys():
            raise KeyError("The configuration does not exist!")
        if name in ["columns","keyfolder","datafolder"]:
            if name == "columns":
                self.__data[name] = ["url","user","comment"]
            else :
                self.__data[name] = setting_config()
        else :
            self.__data.pop(name)
        self.__saveconfig()
        print("Complete removing config {} !".format(name))