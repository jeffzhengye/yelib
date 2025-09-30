# encoding: utf-8
import re

import six
from six import unichr
from bs4 import BeautifulSoup
import pypinyin
from pypinyin import pinyin
from zhconv import convert

__author__ = "jeffye"

"""
Suggestion: convert python str to unicode whenever possible.
"""


def any2utf8(text, errors="strict", encoding="utf8"):
    """Convert a string (unicode or bytestring in `encoding`), to bytestring in utf8.
    only for python 2
    """
    if isinstance(text, unicode):
        return text.encode("utf8")
    # do bytestring -> unicode -> utf8 full circle, to ensure valid utf8
    return unicode(text, encoding, errors=errors).encode("utf8")


to_utf8 = any2utf8


def any2unicode(text, encoding="utf8", errors="strict"):
    """Converts `text` to Unicode (if it's not already), assuming utf-8 input."""
    if six.PY3:
        if isinstance(text, str):
            return text
        elif isinstance(text, bytes):
            return text.decode("utf-8", "ignore")
        else:
            raise ValueError("Unsupported string type: %s" % (type(text)))
    elif six.PY2:
        if isinstance(text, str):
            return text.decode("utf-8", "ignore")
        elif isinstance(text, unicode):
            return text
        else:
            raise ValueError("Unsupported string type: %s" % (type(text)))
    else:
        raise ValueError("Not running on Python2 or Python 3?")


to_unicode = any2unicode

TAG_CLEANER = re.compile("<.*?>")


def clean_html_reg(raw_html):
    clean_text = re.sub(TAG_CLEANER, "", raw_html)
    return clean_text


def clean_html_soup(raw_html):
    clean_text = BeautifulSoup(raw_html).text
    return clean_text


def sentence_split(str_centence):
    list_ret = list()
    for s_str in str_centence.split("."):
        if "?" in s_str:
            list_ret.extend(s_str.split("?"))
        elif "!" in s_str:
            list_ret.extend(s_str.split("!"))
        else:
            list_ret.append(s_str)
    return list_ret


HAN = re.compile(r"^[\u4e00-\u9fa5]+$")

DIG_HYPHEN_DOT = re.compile(r"^[\d\.-_]+")
EN = re.compile(r"^[A-Za-z]+$")
EN_DIG = re.compile(r"^[A-Za-z0-9]+$")
EMAIL = re.compile(r"^\w+([-+.]\w+)*@\w+([-.]\w+)*\.\w+([-.]\w+)*$")
InternetURL = re.compile(r"[a-zA-z]+://[^\s]*")
punctuation = (
    "[\u3002\uff1b\uff0c\uff1a\u201c\u201d\uff08\uff09\u3001\uff1f\u300a\u300b]"
)
PUNCTUATION = re.compile(
    r"^[,，\.·‘~’】【〔〕‰{}〉〈;、。:；\"'!!！|…&★#～？／《》“”：（）―－＋\*+％\(\)\.\:\?\[\]<>\|]+$"
)


def normalize(text):
    text = any2unicode(text)
    if HAN.match(text) or EN.match(text):
        return text
    elif EN_DIG.match(text):
        return "EN_DIG"
    elif DIG_HYPHEN_DOT.match(text):
        return "DIG_HYPHEN_DOT"
    elif EMAIL.match(text):
        return "EMAIL"
    elif InternetURL.match(text):
        return "InternetURL"
    elif PUNCTUATION.match(text):
        return "PUNCTUATION"
    else:
        return "OTHERS"


def is_chinese(uchar):
    """判断一个unicode是否是汉字"""
    if uchar >= "\u4e00" and uchar <= "\u9fa5":
        return True
    else:
        return False


def is_number(uchar):
    """判断一个unicode是否是数字"""
    if uchar >= "\u0030" and uchar <= "\u0039":
        return True
    else:
        return False


def is_alphabet(uchar):
    """判断一个unicode是否是英文字母"""
    if (uchar >= "\u0041" and uchar <= "\u005a") or (
        uchar >= "\u0061" and uchar <= "\u007a"
    ):
        return True
    else:
        return False


def is_other(uchar):
    """判断是否非汉字，数字和英文字符"""
    if not (is_chinese(uchar) or is_number(uchar) or is_alphabet(uchar)):
        return True
    else:
        return False


def B2Q(uchar):
    """半角转全角"""
    inside_code = ord(uchar)
    if inside_code < 0x0020 or inside_code > 0x7E:  # 不是半角字符就返回原来的字符
        return uchar
    if inside_code == 0x0020:  # 除了空格其他的全角半角的公式为:半角=全角-0xfee0
        inside_code = 0x3000
    else:
        inside_code += 0xFEE0
    return unichr(inside_code)


def Q2B(uchar):
    """全角转半角"""
    inside_code = ord(uchar)
    if inside_code == 0x3000:
        inside_code = 0x0020
    else:
        inside_code -= 0xFEE0
    if inside_code < 0x0020 or inside_code > 0x7E:  # 转完之后不是半角字符返回原来的字符
        return uchar
    return unichr(inside_code)


def stringQ2B(ustring):
    """把字符串全角转半角"""
    return "".join([Q2B(uchar) for uchar in ustring])


def uniform(ustring):
    """格式化字符串，完成全角转半角，大写转小写的工作"""
    return stringQ2B(ustring).lower()


def string2List(ustring):
    """将ustring按照中文，字母，数字分开"""
    retList = []
    utmp = []
    for uchar in ustring:
        if is_other(uchar):
            if len(utmp) == 0:
                continue
            else:
                retList.append("".join(utmp))
                utmp = []
        else:
            utmp.append(uchar)
    if len(utmp) != 0:
        retList.append("".join(utmp))
    return retList


class CHARTYPE:
    LETTER = 1
    CJK = 2
    DIGIT = 3
    OTHER = 4


# CHARTYPE = enum(LETTER=1, CJK=2, DIGIT=3, OTHER=4)


def getType(c):
    if is_number(c):
        return CHARTYPE.DIGIT
    elif is_alphabet(c):
        return CHARTYPE.LETTER
    return CHARTYPE.OTHER


def remove_punctuation(strs):
    """
    去除标点符号
    :param strs:
    :return:
    """
    return re.sub(
        r"[\s+\.\!\/<>“”,$%^*(+\"\']+|[+——！，。？、~@#￥%……&*（）]+", "", strs.strip()
    )


def traditional2simplified(sentence):
    """
    将sentence中的繁体字转为简体字
    :param sentence: 待转换的句子
    :return: 将句子中繁体字转换为简体字之后的句子
    """
    return convert(sentence, "zh-hans")


def simplified2traditional(sentence):
    """
    将sentence中的简体字转为繁体字
    :param sentence: 待转换的句子
    :return: 将句子中简体字转换为繁体字之后的句子
    """
    return convert(sentence, "zh-hant")


def get_homophones_by_char(input_char):
    """
    根据汉字取同音字
    :param input_char:
    :return:
    """
    result = []
    # CJK统一汉字区的范围是0x4E00-0x9FA5,也就是我们经常提到的20902个汉字
    for i in range(0x4E00, 0x9FA6):
        if (
            pinyin([chr(i)], style=pypinyin.NORMAL)[0][0]
            == pinyin(input_char, style=pypinyin.NORMAL)[0][0]
        ):
            result.append(chr(i))
    return result


def get_homophones_by_pinyin(input_pinyin):
    """
    根据拼音取同音字
    :param input_pinyin:
    :return:
    """
    result = []
    # CJK统一汉字区的范围是0x4E00-0x9FA5,也就是我们经常提到的20902个汉字
    for i in range(0x4E00, 0x9FA6):
        if pinyin([chr(i)], style=pypinyin.TONE2)[0][0] == input_pinyin:
            # TONE2: 中zho1ng
            result.append(chr(i))
    return result


def tokenize_chinese_by_character(query):
    bufIndex = 0
    retList = []
    buf = []
    preType = -1
    for i in range(0, len(query)):
        c = query[i]
        curType = getType(c)
        if curType is CHARTYPE.DIGIT or curType is CHARTYPE.LETTER:
            if len(buf) > 0:
                if preType == curType:
                    buf.append(c)
                else:
                    retList.append("".join(buf))
                    buf = []
                    buf.append(c)
            else:
                buf.append(c)
        else:
            if len(buf) > 0:
                retList.append("".join(buf))
                buf = []
            if len(c.strip()) > 0:
                retList.append(c)
        preType = curType
    if len(buf) > 0:
        token = "".join(buf)
        if len(token.strip()) > 0:
            retList.append("".join(buf))
    return retList


if __name__ == "__main__":
    print(HAN.match("中国"))
    print(HAN.match("中z"))
    print(DIG_HYPHEN_DOT.match("18.9876h"))
    print(PUNCTUATION.match(".[<|"))
    print(tokenize_chinese_by_character("中国hello, kitty"))

    import random
    import pickle

    cjb = []
    for i in range(5):
        name = input("name:")  # 姓名
        cj = random.randint(50, 100)  # 随机生成50——100之间的整数作为成绩
        cjb.append([name, cj])
    print(cjb)

    # 将成绩表中的数据保存到cjb.txt文件中
    with open("cjb.txt", "wb") as f:
        pickle.dump(cjb, f)
