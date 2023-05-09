import os
import shelve
from threading import Thread, RLock

from utils import get_logger, get_urlhash, normalize
from scraper import is_valid
from collections import defaultdict
from tokenize_url import token_url
import re
from urllib.parse import urlparse


class Frontier(object):
    def __init__(self, config, restart, word_map=defaultdict(int), unique_count=0, ics_dict={}, cs_dict={}, stat_dict={}, inf_dict={}, polite_dict={}, max_len=0, longest_url=''):
        self.logger = get_logger("FRONTIER")
        self.config = config
        self.to_be_downloaded = list()
        ####
        self.unique_count = 0
        self.word_map = defaultdict(int)  # frequency of words

        self.ics_dict = {}
        self.cs_dict = {}
        self.stat_dict = {}
        self.inf_dict = {}
        self.polite_dict = {}
        self.max_len = 0
        self.longest_url = ''

        self.lock = RLock()  # new

        ####
        if not os.path.exists(self.config.save_file) and not restart:
            # Save file does not exist, but request to load save.
            self.logger.info(
                f"Did not find save file {self.config.save_file}, "
                f"starting from seed.")
        elif os.path.exists(self.config.save_file) and restart:
            # Save file does exists, but request to start from seed.
            self.logger.info(
                f"Found save file {self.config.save_file}, deleting it.")
            os.remove(self.config.save_file)
        # Load existing save file, or create one if it does not exist.
        self.save = shelve.open(self.config.save_file)
        if restart:
            for url in self.config.seed_urls:
                self.add_url(url)
        else:
            # Set the frontier state with contents of save file.
            self._parse_save_file()
            if not self.save:
                for url in self.config.seed_urls:
                    self.add_url(url)

    def _parse_save_file(self):
        ''' This function can be overridden for alternate saving techniques. '''
        total_count = len(self.save)
        tbd_count = 0
        for url, completed in self.save.values():
            if not completed and is_valid(url):
                self.to_be_downloaded.append(url)
                tbd_count += 1
        self.logger.info(
            f"Found {tbd_count} urls to be downloaded from {total_count} "
            f"total urls discovered.")

    def get_tbd_url(self):

        with self.lock:  # for mulithreading, ENSURES ONLY 1 WORKER CAN POP OFF THE QUEUE AT A TIME
            try:
                return self.to_be_downloaded.pop()
            except IndexError:
                return None

    def add_url(self, url):
        url_temp = url
        url = normalize(url)

        urlhash = get_urlhash(url)

        # avoid being stuck in archive page with filters for too long
        if ("archive.ics.uci.edu/ml/datasets.php" in str(url)) and (len(urlparse(url).query) != 0):
            return False

        # avoid being stuck in gitlab commits
        if ("gitlab.ics.uci.edu" in str(url)) and ("/commit" in str(url)):
            return False

        # avoid tons of genome data thats mostly unreadable for users
        if "cbcl.ics.uci.edu" in str(url):
            return False

        if urlhash not in self.save:
            words, url_len, simhash_obj, is_run = token_url(
                url_temp)

            url_dict = {}
            if is_run:
                pattern1 = r'^.*\.ics\.uci\.edu.*$'
                pattern2 = r'^.*\.cs\.uci\.edu.*$'
                pattern3 = r'^.*\.informatics\.uci\.edu.*$'
                pattern4 = r'^.*\.stat\.uci\.edu.*$'

                if re.match(pattern1, url_temp):
                    url_dict = self.ics_dict
                elif re.match(pattern2, url_temp):
                    url_dict = self.cs_dict
                elif re.match(pattern3, url_temp):
                    url_dict = self.inf_dict
                elif re.match(pattern4, url_temp):
                    url_dict = self.stat_dict

                is_dupe = False
                # if is_enough:
                for k, v in url_dict.items():
                    hamming_distance = v.distance(simhash_obj)
                    # Normalize to a similarity score between 0 and 1
                    similarity_score = 1 - (hamming_distance / 64)

                    if similarity_score > 0.86:
                        is_dupe = True
                        print("DUPE NOT ADDING!!! SIMILARITY SCORE IS:", similarity_score,
                              str(url), "AND", str(k))
                        break

                with self.lock:  # FOR MULTITHREADING ,  ENSURES THAT ONLY 1 WORKER CAN ACCESS AND UPDATE DATA AT A TIME

                    if not is_dupe:
                        # if isn't dupe,
                        # adds the tokens into the data
                        for word in words:
                            self.word_map[word] += 1
                            # below snippet of code is updating the longest url content and length

                        # add simhash to dictionary
                        url_dict[url_temp] = simhash_obj

                        # and adds to the frontier
                        print("Adding:", url, "To Frontier")
                        self.to_be_downloaded.append(url)

                    # no matter what, check if its the longest url
                    if url_len > self.max_len:
                        self.longest_url = url_temp
                        self.max_len = url_len

            self.save[urlhash] = (url, False)
            self.save.sync()
            self.unique_count += 1

        self.logger.info(
            f"Reached {url}.")

    def mark_url_complete(self, url):
        urlhash = get_urlhash(url)
        if urlhash not in self.save:
            # This should not happen.
            self.logger.error(
                f"Completed url {url}, but have not seen it before.")

        with self.lock:
            self.save[urlhash] = (url, True)
            self.save.sync()
