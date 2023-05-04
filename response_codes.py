import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from urllib.parse import urlparse
import re
from utils.download import download


def get_response_code(url):
    try:
        response = requests.get(url)
        return response.status_code
    except requests.exceptions.RequestException as e:
        print("An error occurred:", e)


def extract_links(url, status):
    ret_links = []

    # WE NEED TO HANDLE DIFFERENT VALID RESPONSE CODES

    if status in (200, 201, 301):
        # print("Successfully connected")
        response = requests.get(url)
        html_content = response.text
        soup = BeautifulSoup(html_content,
                             'html.parser')

        for link in soup.find_all('a'):
            newLink = link.get('href')
            newLink = str(newLink)
            newLink = re.sub(r'#.*$', '', newLink)  # remove fragment
            if not (newLink.startswith('http://') or newLink.startswith('https://')):
                newLink = urljoin(url, newLink)
                # detect relative link
            ret_links.append(newLink)

    return ret_links


def get_final_response(url):
    try:
        max_redirects = 5
        response = requests.get(url)

        while response.status_code in (301, 302) and max_redirects > 0:
            print("REDIRECT")
            redirect_url = response.headers.get('Location')
            response = requests.get(redirect_url)
            max_redirects -= 1

        return response

    except requests.exceptions.RequestException as e:
        print("An error occurred:", e)


if __name__ == "__main__":
    # url = "https://www.ics.uci.edu/"
    # url = "https://campusgroups.uci.edu/home/groups/"
    url = "https://campusgroups.uci.edu/club_signup"
    response_code = get_response_code(url)
    print("Response code:", response_code)
    ret_links = extract_links(url, response_code)
    print("Links:", ret_links)
    for link in ret_links:
        print(link, ":", get_response_code(link))

    # with open("crawl_results.txt", "w+") as f:
    #     f.write("THIS MANY UNIQUE URLS:\n")

    #     f.write("This is the most common words dictionary:\n")

    #     f.write("Amount of SubDomains for ics.uci.edu:\n")
    # final_response = get_final_response(url)
    # print("Final URL:", final_response.url)
    # print("Final Response Code:", final_response.status_code)
