# encoding: utf-8
from BeautifulSoup import BeautifulSoup
import re

__author__ = 'jeffye'

"""
Suggestion: convert python str to unicode whenever possible.
"""


def any2utf8(text, errors='strict', encoding='utf8'):
    """Convert a string (unicode or bytestring in `encoding`), to bytestring in utf8.
    """
    if isinstance(text, unicode):
        return text.encode('utf8')
    # do bytestring -> unicode -> utf8 full circle, to ensure valid utf8
    return unicode(text, encoding, errors=errors).encode('utf8')


to_utf8 = any2utf8


def any2unicode(text, encoding='utf8', errors='strict'):
    """Convert a string (bytestring in `encoding` or unicode), to unicode."""
    if isinstance(text, unicode):
        return text
    return unicode(text, encoding, errors=errors)


to_unicode = any2unicode

TAG_CLEANER = re.compile('<.*?>')


def clean_html_reg(raw_html):
    clean_text = re.sub(TAG_CLEANER, '', raw_html)
    return clean_text


def clean_html_soup(raw_html):
    clean_text = BeautifulSoup(raw_html).text
    return clean_text


def sentence_split(str_centence):
    list_ret = list()
    for s_str in str_centence.split('.'):
        if '?' in s_str:
            list_ret.extend(s_str.split('?'))
        elif '!' in s_str:
            list_ret.extend(s_str.split('!'))
        else:
            list_ret.append(s_str)
    return list_ret


HAN = re.compile(u"^[\u4e00-\u9fa5]+$")

DIG_HYPHEN_DOT = re.compile(u"^[\d\.-_]+")
EN = re.compile(u"^[A-Za-z]+$")
EN_DIG = re.compile(u"^[A-Za-z0-9]+$")
EMAIL = re.compile(u"^\w+([-+.]\w+)*@\w+([-.]\w+)*\.\w+([-.]\w+)*$")
InternetURL = re.compile(u"[a-zA-z]+://[^\s]*")
punctuation = "[\u3002\uff1b\uff0c\uff1a\u201c\u201d\uff08\uff09\u3001\uff1f\u300a\u300b]"
PUNCTUATION = re.compile(u"^[,，\.·‘~’】【〔〕‰{}〉〈;、。:；\"'!!！|…&★#～？／《》“”：（）―－＋\*+％\(\)\.\:\?\[\]<>\|]+$")


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
    if uchar >= u'\u4e00' and uchar <= u'\u9fa5':
        return True
    else:
        return False


def is_number(uchar):
    """判断一个unicode是否是数字"""
    if uchar >= u'\u0030' and uchar <= u'\u0039':
        return True
    else:
        return False


def is_alphabet(uchar):
    """判断一个unicode是否是英文字母"""
    if (uchar >= u'\u0041' and uchar <= u'\u005a') or (uchar >= u'\u0061' and uchar <= u'\u007a'):
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
    if inside_code < 0x0020 or inside_code > 0x7e:  # 不是半角字符就返回原来的字符
        return uchar
    if inside_code == 0x0020:  # 除了空格其他的全角半角的公式为:半角=全角-0xfee0
        inside_code = 0x3000
    else:
        inside_code += 0xfee0
    return unichr(inside_code)


def Q2B(uchar):
    """全角转半角"""
    inside_code = ord(uchar)
    if inside_code == 0x3000:
        inside_code = 0x0020
    else:
        inside_code -= 0xfee0
    if inside_code < 0x0020 or inside_code > 0x7e:  # 转完之后不是半角字符返回原来的字符
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


class CHARTYPE():
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


def tokenize_chinese_by_character(query):
    assert (type(query) == unicode)
    bufIndex = 0
    retList = []
    buf = []
    preType = -1
    for i in xrange(0, len(query)):
        c = query[i]
        curType = getType(c)
        if curType is CHARTYPE.DIGIT or curType is CHARTYPE.LETTER:
            if len(buf) > 0:
                if preType == curType:
                    buf.append(c)
                else:
                    retList.append(''.join(buf))
                    buf = []
                    buf.append(c)
            else:
                buf.append(c)
        else:
            if len(buf) > 0:
                retList.append(''.join(buf))
                buf = []
            if len(c.strip()) > 0:
                retList.append(c)
        preType = curType
    if len(buf) > 0:
        token = ''.join(buf)
        if len(token.strip()) > 0:
            retList.append(''.join(buf))
    return retList


if __name__ == '__main__':
    print HAN.match(u'中国')
    print HAN.match(u"中z")
    print DIG_HYPHEN_DOT.match('18.9876h')
    print PUNCTUATION.match(".[<|")
