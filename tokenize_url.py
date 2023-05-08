from nltk.corpus import stopwords
from simhash import Simhash
import nltk
import ssl
from nltk.tokenize import RegexpTokenizer
from bs4 import BeautifulSoup
from utils.download import download
import requests
from bs4 import BeautifulSoup

from collections import defaultdict

from urllib.parse import urlparse


ssl._create_default_https_context = ssl._create_unverified_context
nltk.download('punkt')
nltk.download('stopwords')


def token_url(url):
    try:
        response = requests.get(url)
        try:
            if (response.headers.get('Content-Length')/(1024*1024) > 5):
                return ([], 0, Simhash(""), False)
                # too big! do not download
        except:
            print("Content-Length not in Header of ", url)
            pass

        html_content = response.text
        soup = BeautifulSoup(html_content,
                             'html.parser')

        simhash_obj = Simhash(soup.get_text())

        tokenizer = RegexpTokenizer(r'\w+')
        tokens = tokenizer.tokenize(soup.get_text())  # all the words

        url_len = len(tokens)  # total tokens
        unique_len = len(set(tokens))    # only the unique ones

        info_val = unique_len / url_len
        if (info_val > 0.2) and (unique_len > 140):

            # getting all stopwords in English
            stop_words = set(stopwords.words('english'))
            tokens_without_stop_words = [
                word for word in tokens if word.lower() not in stop_words]
            # Calculate frequency of words

            return (tokens_without_stop_words, url_len, simhash_obj, True)
        else:
            print("LOW INFO! NO ADD:", str(url),
                  "INFO VAL: ", info_val, "LENGTH:", unique_len)
            return ([], 0, simhash_obj, False)
        # if we dont want to add to the frontier and scrape for links, this returns false in the last spot?
    except:
        print("Could Not Tokenize:", str(url))
        return ([], 0, Simhash(""), False)


if __name__ == "__main__":

    # "http://sli.ics.uci.edu/Classes/2013-iCamp?action=login"
    # try:
    #     r = requests.head(
    #         "http://sli.ics.uci.edu/Classes/2013-iCamp?action=download&upname=yelp_data.zip")
    #     print(r.status_code)
    #     # prints the int of the status code. Find more at httpstatusrappers.com :)
    # except requests.ConnectionError:
    #     print("failed to connect")

    # print(len(urlparse("https://archive.ics.uci.edu/ml/datasets.php").query))
    # response = requests.get("https://archive.ics.uci.edu/ml/datasets.php")

    response = requests.get(
        "https://cbcl.ics.uci.edu/public_data/shilab/forColleen/rMATs/colleen-hind-ctrl-KO-mm9/SAMPLE_1/REP_1/Chimeric.out.sam")

    print("testing")
    html_content = response.text
    soup = BeautifulSoup(html_content,
                         'html.parser')
    tokenizer = RegexpTokenizer(r'\w+')
    tokens = tokenizer.tokenize(soup.get_text())  # all the words
    words = defaultdict(int)
    print(tokens)
    print(len(tokens))
    for word in tokens:
        words[word] += 1

    # print(sorted(dict(words).items(),
    #       key=lambda item: item[1], reverse=True)[:100])
    # # print("PRINTING SET")
    # # print(len(set(tokens)))

    # # # # Example usage
    # url = "https://www.informatics.uci.edu/"
    # url1 = "https://www.ics.uci.edu/"
    # response = requests.get(url)
    # html_content = response.text
    # soup = BeautifulSoup(html_content,
    #                      'html.parser', from_encoding="utf-8")
    # response1 = requests.get(url1)
    # html_content1 = response1.text
    # soup1 = BeautifulSoup(html_content1,
    #                       'html.parser')

    # simhash_obj = Simhash(soup.get_text())
    # simhash_obj1 = Simhash(soup1.get_text())

    # # simhash_obj = Simhash("")
    # # # simhash_obj1 = Simhash("testing a string asdk")

    # hamming_distance = simhash_obj1.distance(simhash_obj)
    # # Normalize to a similarity score between 0 and 1
    # similarity_score = 1 - (hamming_distance / 64)
    # print(similarity_score)

    # # tokenizer = RegexpTokenizer(r'\w+')
    # # tokens = tokenizer.tokenize(soup.get_text())

    # # print(tokens)

    # # token_url(text1)
