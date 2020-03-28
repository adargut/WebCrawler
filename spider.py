from bs4 import BeautifulSoup
from queue import Queue
import requests
import re


class WebCrawler:
    def __init__(self, start_url, query, link_cap):
        self.start_url = start_url
        self.query = query
        self.query_location = None
        self.query_found = False
        self.links_queue = Queue()
        self.parser = 'html.parser'  # parser for beautiful soup
        self.link_cap = link_cap  # prevent crawler from running forever
        self.links_visited = 0

    def scrape(self, page_url):
        self.links_visited += 1
        data = requests.get(page_url).text
        soup = BeautifulSoup(data, self.parser)
        search_over = soup.findAll(text=re.compile(self.query))

        if search_over:  # found query expression in current page
            self.query_found = True
            self.query_location = page_url
        else:
            for link in soup.find_all(attrs={'href': re.compile("http")}):
                self.links_queue.put(link.get('href'))

    def crawl(self):
        while not self.query_found and not self.links_queue.empty() and self.links_visited < self.link_cap:
            curr_url = self.links_queue.get()
            self.scrape(curr_url)

        if self.query_found:
            print('### SUCCESS! ###')
            print("Found query at url", self.query_location, "after visiting", self.links_visited, "links")
        else:
            print('### FAILURE! ###')
            print("Could not find query even after visitng", self.links_visited, "links")

    def start(self):
        self.links_queue.put(self.start_url)
        self.crawl()


def main():
    print("Desired start url:")
    url = input()
    print("Desired query:")
    query = input()
    print("Maximum number of links to visit in search of query:")
    link_cap = int(input())

    web_crawler = WebCrawler(url, query, link_cap)
    web_crawler.start()


if __name__ == '__main__':
    main()
