from threading import Thread

from inspect import getsource
from utils.download import download
from utils import get_logger
import scraper
import time
import re

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


class Worker(Thread):
    def __init__(self, worker_id, config, frontier):
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

        while True:
            tbd_url = self.frontier.get_tbd_url()
            print("Got TBD_URL")

            if not tbd_url:
                self.logger.info("Frontier is empty. Stopping Crawler.")
                self.frontier.mark_url_complete(tbd_url)
                print("THIS MANY UNIQUE URLS:", self.frontier.unique_count)
                ####
                print("This is the most common words dictionary:",
                      sorted(dict(self.frontier.word_map).items(), key=lambda item: item[1], reverse=True)[:50])
                print("This is the longest URL",
                      self.frontier.longest_url, "at len", self.frontier.max_len)
                print("Amount of SubDomains for ics.uci.edu:",
                      len(self.frontier.ics_dict.keys()))
                try:
                    with open("crawl_results.txt", "w+") as f:
                        f.write("THIS MANY UNIQUE URLS:",
                                self.frontier.unique_count, "\n")

                        f.write("This is the most common words dictionary:",
                                sorted(dict(self.frontier.word_map).items(), key=lambda item: item[1], reverse=True)[:100], "\n")

                        f.write("Amount of SubDomains for ics.uci.edu: " +
                                len(self.frontier.ics_dict.keys()) + "\n")
                except:
                    pass

                break

            try:
                resp = download(tbd_url, self.config, self.logger)
                if (resp.status == 302 or resp.status == 301):
                    for i in range(1, 5):
                        resp = download(resp.headers.get('Location'),
                                        self.config, self.logger)  # detect redirects

                        if (resp.status != 302 and resp.status != 301):
                            break
                # advance thru at most 5 redirects. if it reaches 5, allow scraper to fail this

                self.logger.info(
                    f"Downloaded {tbd_url}, status <{resp.status}>, "
                    f"using cache {self.config.cache_server}.")

                scraped_urls = scraper.scraper(tbd_url, resp)

                for scraped_url in scraped_urls:
                    self.frontier.add_url(scraped_url)
            except:
                pass

            time.sleep(self.config.time_delay)
