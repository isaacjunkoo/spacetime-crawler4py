from threading import Thread
from inspect import getsource
from utils.download import download
from utils import get_logger
import scraper
import time
import re
# below imports are for sitemaps
import requests
import xml.etree.ElementTree as ET
from urllib.parse import urlparse

import traceback


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
        # print("ENTERED WORKER RUN")
        # OUR CHANGES:

        while True:
            tbd_url = self.frontier.get_tbd_url()
            print("Got TBD_URL")

            if not tbd_url:
                self.logger.info("Frontier is empty. Stopping Crawler.")

                print("THIS MANY UNIQUE URLS:", self.frontier.unique_count)
                ####
                print("This is the most common words dictionary:",
                      sorted(dict(self.frontier.word_map).items(), key=lambda item: item[1], reverse=True))
                print("This is the longest URL",
                      self.frontier.longest_url, "at len", self.frontier.max_len)
                print("Amount of SubDomains for ics.uci.edu:",
                      len(self.frontier.ics_dict.keys()))
                try:
                    with open("crawl_results.txt", "w+") as f:
                        f.write("THIS MANY UNIQUE URLS:",
                                self.frontier.unique_count, "\n")

                        f.write("This is the most common words dictionary:",
                                sorted(dict(self.frontier.word_map).items(), key=lambda item: item[1], reverse=True), "\n")

                        f.write("Amount of SubDomains for ics.uci.edu: " +
                                len(self.frontier.ics_dict.keys()) + "\n")
                except:
                    pass

                break

            try:
                # print("DEBUG 1 STATEMENT")
                with self.frontier.lock:  # FOR MULTITHREADING
                    # print("DEBUG 2 STATEMENT")
                    if tbd_url in self.frontier.polite_dict:    # if url has already been dowloaded
                        # find time since last request
                        time_since_last_req = time.monotonic(
                        ) - self.frontier.polite_dict[tbd_url]
                        if time_since_last_req > 0.6:  # if its less than 0.5 ms
                            # then sleep
                            print("sleeping between workers for politeness")
                            time.sleep(max(0, 0.6 - time_since_last_req))

                    # download url then
                    resp = download(tbd_url, self.config, self.logger)
                    # update the time again
                    self.frontier.polite_dict[tbd_url] = time.monotonic()
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

                with self.frontier.lock:
                    # sitemap_links = []
                    for scraped_url in scraped_urls:
                        self.frontier.add_url(scraped_url)

                    # new code for adding sitemaps to frontier after checking robots.txt access:
                    try:
                        # print("DEBUG 3 STATEMENT")
                        parsed_url = urlparse(tbd_url)
                        root_url = parsed_url.scheme + "://" + parsed_url.netloc
                        sitemap_host_url = root_url + "/sitemap.xml"
                        sitemap_response = requests.get(sitemap_host_url)
                        xml = ET.fromstring(sitemap_response.content)

                        # Extract the URLs from the sitemap
                        sitemap_urls = [elem.text for elem in xml.findall(
                            ".//{http://www.sitemaps.org/schemas/sitemap/0.9}loc")]
                        for sitemap_url in sitemap_urls:
                            if sitemap_url not in self.save:
                                self.frontier.add_url(sitemap_url)
                    except:
                        pass

            except:
                error_msg = traceback.format_exc()
                print(error_msg)
                pass

            with self.frontier.lock:
                self.frontier.mark_url_complete(tbd_url)
            time.sleep(self.config.time_delay)
