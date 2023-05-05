import re
from urllib.parse import urlparse
from urllib.parse import urljoin
from urllib import robotparser
from bs4 import BeautifulSoup
import ssl


def scraper(url, resp):
    """be polite
    url: a string that was previously in the frontier
    resp:
    return: a list of strings

    """
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

    ret_links = []

    # WE NEED TO HANDLE DIFFERENT VALID RESPONSE CODES

    if resp.status == 200:
        # print("Successfully connected")
        soup = BeautifulSoup(resp.raw_response.content,
                             'html.parser', from_encoding="iso-8859-1")
        for link in soup.find_all('a'):
            newLink = link.get('href')
            newLink = str(newLink)
            newLink = re.sub(r'#.*$', '', newLink)  # remove fragment
            if not (newLink.startswith('http://') or newLink.startswith('https://')):
                newLink = urljoin(resp.raw_response.url, newLink)
                # detect relative link
            ret_links.append(newLink)

    else:
        print("Failed to connect")

    return ret_links


def is_valid(url) -> bool:
    # Decide whether to crawl this url or not.
    # If you decide to crawl it, return True; otherwise return False.
    # There are already some conditions that return False.
    try:
        # !!!! CAN ONLY CRAWL THESE !!!!
        #      *.ics.uci.edu/*
        #      *.cs.uci.edu/*
        #   *.informatics.uci.edu/*
        #      *.stat.uci.edu/*

        parsed = urlparse(url)
        # if not an http or https link (if the scheme isnt http or https...), return false
        # print("parsed scheme: ", parsed.scheme)
        if parsed.scheme not in set(["http", "https"]):
            return False

        # checks if domain+path are within the constraints mentioned above
        domain = parsed.netloc
        path = parsed.path
        pattern1 = r'^.*\.ics\.uci\.edu.*$'
        pattern2 = r'^.*\.cs\.uci\.edu.*$'
        pattern3 = r'^.*\.informatics\.uci\.edu.*$'
        pattern4 = r'^.*\.stat\.uci\.edu.*$'
        if not re.match(pattern1, domain + path) and \
                not re.match(pattern2, domain + path) and \
                not re.match(pattern3, domain + path) and \
                not re.match(pattern4, domain+path):
            return False

        robot_protocol = "/robots.txt"

        # get domain
        root_domain = parsed.netloc
        # print(root_domain)

        # assemble  ==> scheme://domain/robots.txt
        root_domain = parsed.scheme + "://" + root_domain + robot_protocol

        # used to parse through robots.txt
        robot_parser = robotparser.RobotFileParser()

        ssl._create_default_https_context = ssl._create_unverified_context

        try:
            robot_parser.set_url(root_domain)
            robot_parser.read()

        except:
            return False

        # if can't fetch this url, return false
        if not robot_parser.can_fetch("*", url):
            # print("Robot not allowed")
            return False

        # if the hyperlink url to another location is any of the things below, return false

        return not re.match(
            r".*\.(css|js|bmp|gif|jpe?g|ico"
            + r"|png|tiff?|mid|mp2|mp3|mp4"
            + r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf|imzml"
            + r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names|root"
            + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso|rdata|rds|matvar"
            + r"|epub|dll|cnf|tgz|sha1|flac|key|gct|mpg|nc|nc4|mrc|mrcs|pkl|lsm"
            + r"|thmx|mso|arff|rtf|jar|csv|dcm|obj|stl|mzml|mzxml|sbml|sim|simdata|odt|czi|mat|czi"
            + r"|rm|smil|wmv|swf|wma|zip|rar|gz|py|cpp|hpp|c|h|sh|cc|java|js|rawdata|fasta"
            + r"|bigwig|bw|bai|bam|ppsx|pps|bam|fastq|vcf|tif|bed|fits|nc|mtx|h5|hdf5|fast5|raw|pdb|csv|tsv)$", url)

        # after error checking:
    except TypeError:
        print("TypeError for ", parsed)
        raise


if __name__ == "__main__":
    print(is_valid("https://www.ics.uci.edu/~dylanlv/index"))
    print("dylanlv:", is_valid("https://www.ics.uci.edu/~dylanlv/index.html"))

    """
    # links = extract_next_links("http://sli.ics.uci.edu/Classes/2016W-178", resp)
    ret_links = []
    response = requests.get("http://sli.ics.uci.edu/Classes/2016W-178")
    html_content = response.text
    soup = BeautifulSoup(html_content,
                         'html.parser', from_encoding="iso-8859-1")
    for link in soup.find_all('a'):
        newLink = link.get('href')
        newLink = str(newLink)
        newLink = re.sub(r'#.*$', '', newLink)  # remove fragment
        if not newLink.startswith('http://') and newLink.startswith('https://'):
            newLink = urljoin(
                "http://sli.ics.uci.edu/Classes/2016W-178", newLink)
            # detect relative link
        ret_links.append(newLink)

    links = []
    for link in ret_links:
        if is_valid(link):
            print("IS VALID", link)
            links.append(link)
        else:
            print("IS NOT VALID:", link)
    # links = [link for link in ret_links if is_valid(link)]
    print(links)

    print(is_valid('http://sli.ics.uci.edu/Classes/2016W-178?action=download&upname=HW1.pdf'))
    print(is_valid("http://computableplant.ics.uci.edu/papers/2006/plcb-02-12-12_Wold.pdf"))
    print(is_valid(
        "https://archive.ics.uci.edu/ml/machine-learning-databases/00222/bank-additional.zip"))
    # test zip, pdf
    """
