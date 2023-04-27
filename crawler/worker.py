from threading import Thread

from inspect import getsource
from utils.download import download
from utils import get_logger
import scraper
import time
from tokenize_url import token_url


class Worker(Thread):
    def __init__(self, worker_id, config, frontier, max_len=0, longest_url=0):
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

                    # url_resp = download(scraped_url, self.config, self.logger)

                    # wait should we be using download again
                    # we're correctly finding the longest url, and we're parsing the words correctly returning
                    # a good dict of words
                    #

                    words, url_len = token_url(
                        scraped_url, self.config, self.logger)
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

            break
            time.sleep(self.config.time_delay)
