import re
from urllib.parse import urlparse
# import urllib.robotparser
from urllib import robotparser
from utils.response import Response
from bs4 import BeautifulSoup
# from crawler.frontier import Frontier


def scraper(url, resp):
    """be polite
    url: a string that was previously in the frontier
    resp:
    return: a list of strings

    """
    print("CALLING SCRAPER.SCRAPER")
    print(url)
    links = extract_next_links(url, resp)
    return [link for link in links if is_valid(link)]


def extract_next_links(url, resp):
    # Implementation required.
    # url: the URL that was used to get the page
    # resp.url: the actual url of the page
    # resp.status: the status code returned by the server. 200 is OK, you got the page. Other numbers mean that there was some kind of problem.
    # resp.error: when status is not 200, you can check the error here, if needed.
    # resp.raw_response: this is where the page actually is. More specifically, the raw_response has two parts:
    #         resp.raw_response.url: the url, again
    #         resp.raw_response.content: the content of the page!
    # Return a list with the hyperlinks (as strings) scrapped from resp.raw_response.content
    # check if status is 200, if 200 go to resp.raw_response.content and get list of hyperlinks
    print("DEBUG: SEE IF ENTERED")
    ret_links = []
    # resp  # = Response(url)
    print("RESPONSE STATUS:", resp.status)

    if resp.status == 200:
        print("Successfully connected")
        soup = BeautifulSoup(resp.raw_response.content, 'html.parser')
        for link in soup.find_all('a'):
            print("Link found")
            ret_links.append(link.get('href'))
        print("HOW MANY URLS:" + len(ret_links))
    else:
        print("Failed to connect")
        pass

    return ret_links


def is_valid(url) -> bool:
    # Decide whether to crawl this url or not.
    # If you decide to crawl it, return True; otherwise return False.
    # There are already some conditions that return False.
    robot_protocol = "/robots.txt"

    root_domain = urlparse(url).netloc.split(
        ".")[-2] + "." + urlparse(url).netloc.split(".")[-1]  # getting the root domain

    # print(root_domain)  # Output: "example.com"
    root_domain = root_domain + robot_protocol

    # used to parse through robots.txt
    # robot_parser = urllib.robotparser.RobotFileParser()
    robot_parser = robotparser.RobotFileParser()

    robot_parser.set_url(root_domain)

    # if can't fetch this url, return false
    if not robot_parser.can_fetch("*", url):
        return False

    try:
        parsed = urlparse(url)
        # if not an http or https link, return false
        if parsed.scheme not in set(["http", "https"]):
            return False
        # if the hyperlink url to another location is any of the things below, return false
        return not re.match(
            r".*\.(css|js|bmp|gif|jpe?g|ico"
            + r"|png|tiff?|mid|mp2|mp3|mp4"
            + r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
            + r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names"
            + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
            + r"|epub|dll|cnf|tgz|sha1"
            + r"|thmx|mso|arff|rtf|jar|csv"
            + r"|rm|smil|wmv|swf|wma|zip|rar|gz)$", parsed.path.lower())

        # after error checking:

    except TypeError:
        print("TypeError for ", parsed)
        raise
