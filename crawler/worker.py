from threading import Thread

from inspect import getsource
from utils.download import download
from utils import get_logger
import scraper
import time
from similarity import calculate_similarity
from tokenize_url import token_url

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


class Worker(Thread):
    def __init__(self, worker_id, config, frontier, max_len=0, longest_url=''):
        self.logger = get_logger(f"Worker-{worker_id}", "Worker")
        self.config = config
        self.frontier = frontier
        # basic check for requests in scraper
        assert {getsource(scraper).find(req) for req in {
            "from requests import", "import requests"}} == {-1}, "Do not use requests in scraper.py"
        assert {getsource(scraper).find(req) for req in {"from urllib.request import",
                                                         "import urllib.request"}} == {-1}, "Do not use urllib.request in scraper.py"
        super().__init__(daemon=True)

    def run(self):
        print("ENTERED WORKER RUN")
        # OUR CHANGES:

        self.max_len = 0
        self.longest_url = ''

        while True:
            tbd_url = self.frontier.get_tbd_url()
            print("Got TBD_URL")
            if not tbd_url:
                self.logger.info("Frontier is empty. Stopping Crawler.")
                break
            resp = download(tbd_url, self.config, self.logger)

            self.logger.info(
                f"Downloaded {tbd_url}, status <{resp.status}>, "
                f"using cache {self.config.cache_server}.")

            # print("About to SCRAPE")
            scraped_urls = scraper.scraper(tbd_url, resp)
            # print("SCRAPED ENDED")
            # print("SCRAPER LENGTH:", len(scraped_urls))
            for scraped_url in scraped_urls:
                added_url = self.frontier.add_url(scraped_url)
                # add to frontier
                # is this where we tokenize ??
                if added_url:
                    words, url_len, fingerprint = token_url(
                        scraped_url, self.config, self.logger)

                    # domain = parsed.netloc
                    # path = parsed.path
                    # pattern1 = r'^.*\.ics\.uci\.edu\/.*$'
                    # pattern2 = r'^.*\.cs\.uci\.edu\/.*$'
                    # pattern3 = r'^.*\.informatics\.uci\.edu\/.*$'
                    # pattern4 = r'^.*\.stat\.uci\.edu\/.*$'

                    # check the beginning of scraped_url to see which dictionary we compare to
                    # compare each url inside the specific bucket and then
                    # if matches 85% or more:
                    # dont add to frontier but still increment unique urls found by 1
                    # increment using self.frontier.unqiue_count += 1
                    # else:
                    # add to the selected bucket to be referenced again later
                    # increment unique urls by 1
                    # increment using self.frontier.unqiue_count += 1

                    for word in words:
                        self.frontier.word_map[word] += 1
                        # below snippet of code is updating the longest url content and length
                        if url_len > self.max_len:
                            self.longest_url = scraped_url
                            self.max_len = url_len

            self.frontier.mark_url_complete(tbd_url)
            print("THIS MANY UNIQUE URLS:", self.frontier.unique_count)
            ####
            print("This is the most common words dictionary:",
                  sorted(dict(self.frontier.word_map).items(), key=lambda item: item[1], reverse=True)[:50])
            print("This is the longest URL",
                  self.longest_url, "at len", self.max_len)

            # I BROKE HERE REMOVE THIS

            # idk where to add the folloing code but i'll leave it here (detecting text similarity) - Angela

            # text1_processed = " ".join(text1_tokens)
            # text2_processed = " ".join(text2_tokens)

            # vectorizer = TfidfVectorizer()
            # vectors = vectorizer.fit_transform([text1_processed, text2_processed])
            # similarity = cosine_similarity(vectors)

            # BELOW CODE COMPARES the similarity score with a threshold value
            # threshold = 0.8
            # if similarity[0][1] > threshold:
            #     print("The two websites' text content is similar.")
            #     *don't add to list of urls*
            # else:
            #     print("The two websites' text content is not similar.")
            #     *add to list of urls*

            break
            time.sleep(self.config.time_delay)
