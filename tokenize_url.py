from nltk.corpus import stopwords
from fuzzywuzzy import fuzz
from sklearn.metrics.pairwise import cosine_similarity
import nltk
import ssl
from nltk.tokenize import RegexpTokenizer
from bs4 import BeautifulSoup
from utils.download import download


ssl._create_default_https_context = ssl._create_unverified_context
nltk.download('punkt')
nltk.download('stopwords')


def token_url(url, config, logger):

    url_resp = download(url, config, logger)
    # Tokenize the texts

    tokenizer = RegexpTokenizer(r'\w+')
    soup = BeautifulSoup(url_resp.raw_response.content,
                         'html.parser')  # getting content
    # strips all extraneous characters, just words

    fingerprint = fuzz.FuzzyWuzzy().fuzz(soup.get_text())

    tokens = tokenizer.tokenize(soup.get_text())
    url_len = len(tokens)

    # getting all stopwords in English
    stop_words = set(stopwords.words('english'))
    tokens_without_stop_words = [
        word for word in tokens if word.lower() not in stop_words]
    # print(tokens)
    # Calculate frequency of words
    return (tokens_without_stop_words, url_len, fingerprint)


def determineFrequency(url_text):
    pass


if __name__ == "__main__":
    print("Hello")
    # Example usage
    text1 = "Hello, how are you doing today?"
    similarity_score = token_url(text1)
