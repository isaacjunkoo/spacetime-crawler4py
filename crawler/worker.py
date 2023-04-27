from threading import Thread

from inspect import getsource
from utils.download import download
from utils import get_logger
import scraper
import time
from similarity import calculate_similarity
from tokenize_url import token_url
import re

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
                self.frontier.mark_url_complete(tbd_url)
                print("THIS MANY UNIQUE URLS:", self.frontier.unique_count)
                ####
                print("This is the most common words dictionary:",
                      sorted(dict(self.frontier.word_map).items(), key=lambda item: item[1], reverse=True)[:50])
                print("This is the longest URL",
                      self.longest_url, "at len", self.max_len)
                break
            resp = download(tbd_url, self.config, self.logger)

            self.logger.info(
                f"Downloaded {tbd_url}, status <{resp.status}>, "
                f"using cache {self.config.cache_server}.")

            # print("About to SCRAPE")
            scraped_urls = scraper.scraper(tbd_url, resp)
            # print("SCRAPED ENDED")
            # print("SCRAPER LENGTH:", len(scraped_urls))
            url_dict = {}
            for scraped_url in scraped_urls:
                (added_url, urlhash, url) = self.frontier.add_url(scraped_url)
                # add to frontier
                # is this where we tokenize ??
                if added_url:
                    words, url_len, simhash_obj, is_run = token_url(
                        scraped_url, self.config, self.logger)

                    if is_run:
                        pattern1 = r'^.*\.ics\.uci\.edu\/.*$'
                        pattern2 = r'^.*\.cs\.uci\.edu\/.*$'
                        pattern3 = r'^.*\.informatics\.uci\.edu\/.*$'
                        pattern4 = r'^.*\.stat\.uci\.edu\/.*$'

                        if re.match(pattern1, scraped_url):
                            url_dict = self.frontier.ics_dict
                        elif re.match(pattern2, scraped_url):
                            url_dict = self.frontier.cs_dict
                        elif re.match(pattern3, scraped_url):
                            url_dict = self.frontier.inf_dict
                        elif re.match(pattern4, scraped_url):
                            url_dict = self.frontier.stat_dict

                        is_dupe = False
                        for k, v in url_dict.items():
                            hamming_distance = v.distance(simhash_obj)
                            # Normalize to a similarity score between 0 and 1
                            similarity_score = 1 - (hamming_distance / 64)

                            if similarity_score > 0.85:
                                is_dupe = True
                                break

                        if not is_dupe:
                            url_dict[scraped_url] = simhash_obj
                            # self.frontier.save[urlhash] = (url, False)
                            # self.frontier.save.sync()
                            # self.frontier.to_be_downloaded.append(url)

                        self.frontier.unique_count += 1

                        # domain = parsed.netloc
                        # path = parsed.path

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

            # print(url_dict)

            time.sleep(self.config.time_delay)
