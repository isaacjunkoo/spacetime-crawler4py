from threading import Thread

from inspect import getsource
from utils.download import download
from utils import get_logger
import scraper
import time
from tokenize_url import token_url


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

        max_len = 0
        longest_url = ''

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
            print("SCRAPER LENGTH:", len(scraped_urls))
            for scraped_url in scraped_urls:
                added_url = self.frontier.add_url(scraped_url)
                # add to frontier
                # is this where we tokenize ??
                if added_url:
                    words, url_len = token_url(scraped_url)
                    for word in words:
                        self.frontier.word_map[word] += 1
                        if url_len > max_len:
                            longest_url = scraped_url
                            max_url = url_len
            self.frontier.mark_url_complete(tbd_url)

            # I BROKE HERE REMOVE THIS
            break
            time.sleep(self.config.time_delay)
