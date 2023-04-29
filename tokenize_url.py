from nltk.corpus import stopwords
from simhash import Simhash
import nltk
import ssl
from nltk.tokenize import RegexpTokenizer
from bs4 import BeautifulSoup
from utils.download import download
import requests
from bs4 import BeautifulSoup


ssl._create_default_https_context = ssl._create_unverified_context
nltk.download('punkt')
nltk.download('stopwords')


def token_url(url):
    try:
        ####

        response = requests.get(url)
        html_content = response.text
        soup = BeautifulSoup(html_content,
                             'html.parser')
        ####
        tokenizer = RegexpTokenizer(r'\w+')

        simhash_obj = Simhash(soup.get_text())

        tokens = tokenizer.tokenize(soup.get_text())
        url_len = len(tokens)

        # getting all stopwords in English
        stop_words = set(stopwords.words('english'))
        tokens_without_stop_words = [
            word for word in tokens if word.lower() not in stop_words]
        # Calculate frequency of words
        return (tokens_without_stop_words, url_len, simhash_obj, True)
    except:
        print("Could Not Tokenize:", str(url))
        return ([], 0, Simhash(""), False)


if __name__ == "__main__":
    print("Hello")
    # Example usage
    url = "http://archive.ics.uci.edu/ml/datasets.php"
    response = requests.get(url)
    html_content = response.text

    soup = BeautifulSoup(html_content,
                         'html.parser', from_encoding="utf-8")
    tokenizer = RegexpTokenizer(r'\w+')
    tokens = tokenizer.tokenize(soup.get_text())

    print(tokens)

    # token_url(text1)
