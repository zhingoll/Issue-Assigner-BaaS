import re
from nltk.corpus import stopwords
from lxml import etree
import mistune
from nltk.stem.snowball import EnglishStemmer
from nltk.corpus import stopwords


def clean_text(text:str) -> str:
    '''
    Clean text data -> Obtain clean text
    '''
    text = str(text)
    # Convert to lowercase
    text = text.lower()
    # Convert markdown to HTML format
    text = mistune.html(text)
    # Match and remove URLs
    url_pattern_my = re.compile(r"(https?|ftp|file)://[-A-Za-z0-9+&@#/%?=~_|!:,.;]+[-A-Za-z0-9+&@#/%=~_|]")
    text = url_pattern_my.sub(" ", text)
    # Convert HTML to text
    html_tree = etree.HTML(text)
    if html_tree is not None:
        text = html_tree.xpath('string(.)')
    else:
        text = ""  # Return an empty string if the conversion fails
    # Remove all characters except numbers, letters, and whitespace (e.g., emojis)
    text = re.sub(r"[^\w\s]|\_", " ", text)
    # Extract word stems
    text = " ".join([EnglishStemmer().stem(w) for w in text.split()])
    # Remove stopwords
    text = " ".join([w for w in text.split() if w not in set(stopwords.words("english"))])  

    return text

