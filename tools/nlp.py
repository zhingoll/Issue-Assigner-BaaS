import re
from nltk.corpus import stopwords
from lxml import etree
import mistune
from nltk.stem.snowball import EnglishStemmer
from nltk.corpus import stopwords


def clean_text(text:str) -> str:
    '''
    清理文本数据 -> 得到干净的文本
    '''
    # 全小写
    text = text.lower()
    # 将markdown格式转换成HTML格式
    text = mistune.html(text)
    # 匹配并去除URL
    url_pattern_my = re.compile(r"(https?|ftp|file)://[-A-Za-z0-9+&@#/%?=~_|!:,.;]+[-A-Za-z0-9+&@#/%=~_|]")
    text = url_pattern_my.sub(" ", text)
    # 将HTML转换成字符串
    text = etree.HTML(text=text).xpath('string(.)')
    # 去除数字、字母、空白符以外的所有字符（例如表情）
    text = re.sub(r"[^\w\s]|\_", " ", text)
    # 提取词干
    text = " ".join([EnglishStemmer().stem(w) for w in text.split()])
    # 去除停用词
    text = " ".join([w for w in text.split() if w not in set(stopwords.words("english"))])  

    return text

