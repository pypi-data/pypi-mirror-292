from pathlib import Path
from pysswordsz.pzsconfig import pszconfig
from pysswordsz.encrytool import encryting,generatePassword
from uuid import uuid4
from datetime import datetime

import typer

import polars as pl

def buildPWDB(name:str) -> None:
    cons = pszconfig()
    filePlace = cons.datafolder()
    columns = cons.columns
    data = {
        i:[] for i in (["uuid","name"]+columns+["password","createtime"])
    }
    data = pl.DataFrame(data)
    data.write_csv(filePlace / (name+".lyz"))
    cons.setting("vault",name)
    if cons.vaultlist :
        if name in cons.vaultlist :
            raise ValueError("vault {} already exists".format(name))
        else:
            cons.setting("vaultlist",cons.vaultlist.append(name))
    else:
        cons.setting("vaultlist",[name])
    print("Complete build a vault {}".format(name))

def ask_password() -> list :
    resList = {}
    resList["n"] = typer.prompt("输入密码长度 --> ",default=16,type=int)
    is_url = typer.confirm("是否需要URL安全字符? --> ")
    if is_url :
        resList["urlsafe"] = is_url
    else:
        resList["need_number"] = typer.confirm("是否需要数字? --> ",default=True)
        resList["need_upper"] = typer.confirm("是否需要大写字母? --> ",default=True)
        resList["need_punctuation"] = typer.confirm("是否需要符号? --> ",default=True)
        resList["mina"] = typer.prompt("各类型字符的最小个数 --> ",default=1,type=int)
    return resList

class pwsmanager(object):
    def __init__(self) -> None:
        cons = pszconfig()
        self.__home = cons.datafolder()
        self.__default = cons.vault
        self.__vaultList = cons.vaultlist
        self.__cipher = encryting()
        self.__columns = cons.columns
    def __read(self, vault:str) -> pl.DataFrame:
        theVault = self.__default if vault=="default" else vault
        if theVault not in self.__vaultList :
            raise ValueError("vault {} not exists".format(theVault))
        return pl.read_csv(self.__home / (theVault+".lyz"),
                           schema_overrides={"createtime":pl.Datetime})
    def update(self,name:str, vault:str = "default"):
        theVault = self.__default if vault=="default" else vault
        alldata = self.__read(theVault)
        if name not in alldata["name"].unique().to_list():
            raise ValueError("password {} not exists. You need create one".format(name))
        else:
            olddata = alldata.filter(pl.col("name")==name)
        newdata = {
            "uuid":str(uuid4()),
            "name":name}
        for i in self.__columns:
            newdata[i] = olddata.select(pl.col(i)).unique().to_numpy()[0][0]
        if typer.confirm("是否需要直接生成新密码？ --> ") :
            password = generatePassword(n=16)
        else :
            password = generatePassword(**ask_password())
        newdata["password"] = self.__cipher.encrypt_data(password)
        newdata["createtime"] = datetime.now()
        alldata = alldata.vstack(pl.DataFrame(newdata))
        alldata.write_csv(self.__home / (theVault+".lyz"))
        print("Complete updated a password of {} ...".format(name))
    def search(self, name:str, all:bool = False, vault:str = "default"):
        data = self.__read(vault)
        sdata = data.filter(pl.col("name")==name)
        if sdata.is_empty():
            sdata = data.filter(pl.col("name").str.contains(name))
        if sdata.is_empty():
            print("[red]No result found!")
            return pl.DataFrame()
        else:
            sdata = sdata.with_columns(
                password = pl.col("password").map_elements(lambda x : self.__cipher.decrypt_data(x),return_dtype=pl.String)
            )
            if all:
                return sdata.sort("createtime",descending=True)
            else:
                return sdata.sort("createtime",descending=True).head(1)
    def add_password(self,name:str, to:str = "default"):
        theVault = self.__default if to=="default" else to
        if theVault not in self.__vaultList :
            raise ValueError("vault {} not exists".format(theVault))
        add_Data = {
            "uuid":[str(uuid4())],
            "name":[name]}
        for i in self.__columns:
            txt = typer.prompt("please input the {} of {} --> ".format(i,name))
            is_encr = typer.confirm("是否需要加密保存? --> ")
            if is_encr :
                add_Data[i] = [self.__cipher.encrypt_data(txt)]
            else :
                add_Data[i] = [txt]
        if typer.confirm("是否需要生成新密码？ --> ") :
            password = generatePassword(**ask_password())
        else :
            password = typer.prompt("请输入密码 --> ",hide_input=True,confirmation_prompt=True)
        add_Data["password"] = [self.__cipher.encrypt_data(password)]
        add_Data["createtime"] = [datetime.now()]
        alldata = self.__read(to)
        alldata = alldata.vstack(pl.DataFrame(add_Data))
        alldata.write_csv(self.__home / (theVault+".lyz"))
        print("Complete adding a password of {} into {} vault...".format(name, to))
    def delete(self, name:str, vault:str = "default"):
        theVault = self.__default if vault=="default" else vault
        data = self.__read(theVault)
        if name not in data["name"].unique().to_list():
            raise ValueError("password {} not exists.".format(name))
        else:
            data = data.filter(pl.col("name")!=name)
            data.write_csv(self.__home / (theVault+".lyz"))
        print("Complete deleted passwords {} from {} ...".format(name,vault))
    def list(self, vault:str = "default", other_columns:list[str]|None = None):
        alldata = self.__read(vault)
        if other_columns :
            selcols = ["uuid","name"] + other_columns + ["createtime"]
            return alldata.select(pl.col(selcols))
        else:
            return alldata