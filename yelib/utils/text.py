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


if __name__ == '__main__':
    print HAN.match(u'中国')
    print HAN.match(u"中z")
    print DIG_HYPHEN_DOT.match('18.9876h')
    print PUNCTUATION.match(".[<|")

