import random
from secrets import choice
from random_words import RandomWords as engrandwords
from pysswordsz.ChineseWords import CIZU
from pywubi import wubi
from pypinyin import lazy_pinyin, Style

def getChinese() -> str:
    val = random.randint(0x4e00, 0x9fbf)
    return chr(val)

def getChineseWords() -> str:
    length = len(CIZU)
    word = CIZU[random.randint(0, length-1)]
    return word

def transChinese(words:str, ttype:str = "pinyin") -> str:
    if ttype not in ["pinyin", "wubi", "wade"] :
        raise ValueError("mode must be in ['pinyin', 'wubi', 'wade']")
    if ttype == "pinyin":
        res = lazy_pinyin(words)
    elif ttype == "wubi":
        res = wubi(words, single=False)
    else :
        res = lazy_pinyin(words, style=Style.WADEGILES)
        res = [i.replace("'","") for i in res]
    return "".join(res)

class getrandomWords(object):
    TYPEMODE = ["pinyin","wubi","english","wade"]
    def __init__(self, n:int = 8, mode:str = "pinyin", phrase:bool = True):
        if mode not in getrandomWords.TYPEMODE:
            raise ValueError("mode must be in ['pinyin', 'wubi', 'wade', 'english']")
        self.__mode = mode
        self.words = []
        if phrase :
            if mode != "english":
                self.words.extend([getChineseWords() for _ in range(n)])
            else:
                self.words.extend(engrandwords().random_words(count=n))
        else :
            if mode != "english":
                self.words.extend([getChinese() for _ in range(n)])
            else:
                self.words.extend(engrandwords().random_words(count=n))
        self.__keywords = self.words
        if mode != "english" :
            self.words = [transChinese(i, ttype = mode) for i in self.words]
    def __str__(self):
        return self.join()
    def __repr__(self):
        txt = [
            "in '{}' mode:".format(self.__mode.upper()),
            self.join(),
            None if self.__mode == "english" else " ".join(self.__keywords)
        ]
        return txt
    def join(self, seq:str = " ") -> str:
        return seq.join(self.words)
    def first(self) -> str:
        return self.words[0]


def justWord() -> str :
    this_typw = choice(getrandomWords.TYPEMODE)
    return getrandomWords(3, mode = this_typw).first()