import string
import shutil
import polars as pl
from datetime import datetime
import os
from collections.abc import Callable
from secrets import token_urlsafe,randbelow,choice
from random import shuffle
from math import floor,ceil
from typing import Any
from pysswordsz.pzsconfig import pszconfig
from getpass import getpass
from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes,random
from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.IO import PEM
from zipfile import ZipFile,ZIP_DEFLATED
from uuid import uuid3,NAMESPACE_URL
from pathlib import Path
from typer import prompt
from pysswordsz.pzsconfig import belongto
from pysswordsz.getrandwords import getrandomWords,justWord


def hasin(oripart:Callable, target:Any) -> int:
    resn = 0
    for i in oripart :
        if i == target :
            resn = resn + 1
    return resn

def toprandList(top:int, n:int = 4, minz:int = 1) -> list[int] :
    res = []
    loT = floor(top * 2 / 3)
    for i in range(n-1) :
        tx = randbelow(loT)
        if tx < (top / n) and i < 1:
            tx = floor(top / n)
        if tx < minz :
            tx = tx + minz
        res.append(tx)
        loT = floor((top - sum(res)) * 2 / 3)
    if res[0] > (top / 3) :
        res.append(top - sum(res))
    else :
        res = [top - sum(res)] + res
    return res

def randomUpper(word:str):
    sl = len(word)
    n = randbelow(sl)
    return (word[:n]+word[n].upper()+word[n+1:])

def generateXKCDPassword(n:int = 6, type_mode:str = "pinyin",
                         padding:bool = False) -> str :
    if type_mode not in ["pinyin","wubi","english","wade","mix"]:
        raise ValueError("type_mode {} not exists".format(type_mode))
    file = Path(os.path.dirname(__file__)) / "static/{}.wordlist".format(type_mode)
    sep = " " if padding is False else "!@$%^&*-_+=:|~?.;"
    if type_mode == "mix":
        wordlist = [justWord() for _ in range(n)]
    else:
        wordlist = getrandomWords(n, mode = type_mode).words
    wordlist = [randomUpper(i) for i in wordlist]
    if padding :
        xn = ceil(n/4)
        seqList = ["".join(random.sample(sep,xn)) for i in range(n)]
        pw = "".join([seqList[i]+wordlist[i] for i in range(n)]) + "".join(random.sample(sep,xn))
    else:
        pw = sep.join(wordlist)
    return pw

def generatePassword(n:int, need_number:bool = True, 
                     need_upper:bool = True, need_punctuation:bool = True, 
                     mina:int = 1, urlsafe:bool = False) -> str :
    if urlsafe :
        n_x = floor(n / 1.3)
        pw = token_urlsafe(n_x)
        if not belongto(pw, "_-^@()[]") :
            pw = pw.replace(pw[randbelow(n)], "_")
    else :
        partnum = hasin([need_number,need_punctuation,need_upper], True)
        basechars = toprandList(top=n,n=(partnum+1),minz=mina)
        keyChar = [string.ascii_lowercase]
        if need_number :
            keyChar.append(string.digits)
        if need_upper :
            keyChar.append(string.ascii_uppercase)
        if need_punctuation :
            keyChar.append("!~@#$%^&*()_+=-[]|:;?<>,.{}")
        res = []
        for i in range(partnum+1) :
            res = res + [choice(keyChar[i]) for jj in range(basechars[i])]
        shuffle(res)
        shuffle(res)
        pw = "".join(res)
    return pw

def newKeys() -> None:
    print("输入你的主密码。\n但请特别注意：务必记住主密码，一旦丢失主密码，则加密信息和保存的密码将不再能打开！")
    passwordx = prompt("Core Password:", hide_input=True, confirmation_prompt=True)
    print("Waiting for creating the keys...")
    private = RSA.generate(3072)
    keyHome = pszconfig().keyfolder()
    with open(keyHome/"theKey.lyz", "wb") as f:
        data = private.export_key(passphrase=passwordx,
                                pkcs=8,
                                protection='PBKDF2WithHMAC-SHA512AndAES256-CBC',
                                prot_params={'iteration_count':131072})
        f.write(data)
    print("The keys have been created!")
    print("!!Reminder!!\n\tDon't forget your Core Password!")

class encryting(object):
    def __init__(self) -> None:
        passwordx = getpass("Core Password :")
        keyHome = pszconfig().keyfolder()
        self.__dataHome = pszconfig().datafolder()/"encinfoDB.lyz"
        with open(keyHome/"theKey.lyz", "rb") as f:
            data = f.read()
        self.__private = RSA.import_key(data, passphrase=passwordx)
        self.__public = self.__private.public_key()
    def encrypt_data(self, data:str) -> str:
        cipher = PKCS1_OAEP.new(self.__public)
        ciphertext = cipher.encrypt(data.encode("utf-8"))
        return PEM.encode(ciphertext, "DATA")
    def decrypt_data(self, data:str) -> str:
        odata = PEM.decode(data)[0]
        cipher = PKCS1_OAEP.new(self.__private)
        plaintext = cipher.decrypt(odata)
        return plaintext.decode()
    def encrypt_file(self, file:str|Path, comments:str|None = None) -> None:
        oriPath = Path(file)
        if oriPath.is_dir() :
            zipPath = oriPath.parent/("{}.zip".format(oriPath.name))
            with ZipFile(zipPath, 
                         compression = ZIP_DEFLATED, compresslevel = 7,
                         mode = "w") as fz :
                for i in oriPath.glob("*") :
                    fz.write(i, compress_type=ZIP_DEFLATED, compresslevel=7)
            shutil.rmtree(oriPath)
        with open((zipPath if oriPath.is_dir() else oriPath), "rb") as f:
            data = f.read()
        session_key = get_random_bytes(16)
        cipher_rsa = PKCS1_OAEP.new(self.__public)
        enc_session_key = cipher_rsa.encrypt(session_key)
        cipher_aes = AES.new(session_key, AES.MODE_EAX)
        ciphertext, tag = cipher_aes.encrypt_and_digest(data)
        save_name = oriPath.parent/("{}.lyz".format(oriPath.name))
        with open(save_name, "wb") as f:
            f.write(enc_session_key)
            f.write(cipher_aes.nonce)
            f.write(tag)
            f.write(ciphertext)
        thisData = {
             "UUID": [uuid3(NAMESPACE_URL,str(oriPath))],
             "name": [("{}.lyz".format(oriPath.name))],
             "path": [oriPath.parent],
             "type": ["file" if oriPath.is_file() else "folder"],
             "comments": [comments],
             "time": [datetime.now().strftime("%Y-%m-%d %H:%M:%S")]
        }
        encrList = self.list_files()
        encrList = encrList.vstack(pl.from_dicts(thisData))
        encrList.write_csv(self.__dataHome)
        shutil.rmtree((zipPath if oriPath.is_dir() else oriPath))
    def decrypt_file(self, file:str|Path) -> None:
        with open(Path(file), "rb") as f:
            enc_session_key = f.read(self.__private.size_in_bytes())
            nonce = f.read(16)
            tag = f.read(16)
            ciphertext = f.read()
        cipher_rsa = PKCS1_OAEP.new(self.__private)
        session_key = cipher_rsa.decrypt(enc_session_key)
        cipher_aes = AES.new(session_key, AES.MODE_EAX, nonce)
        data = cipher_aes.decrypt_and_verify(ciphertext, tag)
        disname = Path(file).name.replace(".lyz", "")
        if "." in disname :
            save_name = Path(file).parent/disname
        else :
            save_name = Path(file).parent/(disname+".zip")
        with open(save_name, "wb") as f:
            f.write(data)
        shutil.rmtree(Path(file))
        with ZipFile(save_name, "r") as fz :
            fz.extractall(Path(file).parent)
        shutil.rmtree(save_name)
        encrList = self.list_files()
        encrList = encrList.filter(
            pl.col("UUID") != uuid3(NAMESPACE_URL,str(Path(file).parent/disname)))
        encrList.write_csv(self.__dataHome)
    def list_files(self) -> pl.DataFrame:
        if self.__dataHome.exists() :
            return pl.read_csv(self.__dataHome)
        else :
            return pl.DataFrame()


