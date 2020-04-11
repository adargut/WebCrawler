from bs4 import BeautifulSoup
from queue import Queue
import threading
import requests
import logging
import re


class WebCrawler:
    def __init__(self, start_url, query, link_cap, num_of_threads):
        self.start_url = start_url
        self.query_location = None
        self.query_found = False
        self.query = query
        self.num_of_threads = num_of_threads
        self.links_queue = Queue()
        self.parser = 'html.parser'  # parser for beautiful soup
        self.link_cap = link_cap  # prevent crawler from running forever
        self.links_visited = 0
        # Lock mechanism for synchronizing threads
        self._lock1 = threading.Lock()
        self._lock2 = threading.Lock()
        self._l = lambda n: logging.info("thread %s acquired lock%d", threading.current_thread().getName(), n)
        self._u = lambda n: logging.info("thread %s acquired lock%d", threading.current_thread().getName(), n)

    def scrape(self) -> None:
        # CRITICAL SECTION 1 #
        self._lock1.acquire()
        self._l(1)
        if self.links_queue.empty():
            self._lock1.release()
            self._u(1)
            return
        page_url = self.links_queue.get()
        self.links_visited += 1
        self._u(1)
        self._lock1.release()
        # END OF CRITICAL SECTION 1 #

        data = requests.get(page_url).text
        soup = BeautifulSoup(data, self.parser)
        search_over = soup.findAll(text=re.compile(self.query))

        if search_over:  # found query expression in current page
            self.query_found = True
            self.query_location = page_url
            logging.info("Query found by thread %s", threading.current_thread().getName())
        else:
            for link in soup.find_all(attrs={'href': re.compile("http")}):
                # CRITICAL SECTION 2 #
                self._lock2.acquire()
                self._l(2)
                self.links_queue.put(link.get('href'))
                self._u(2)
                self._lock2.release()
                # END OF CRITICAL SECTION 2 #

    def crawl(self) -> None:
        while not self.query_found and self.links_visited < self.link_cap:
            self.scrape()

    def start(self) -> None:
        self.links_queue.put(self.start_url)
        for idx in range(self.num_of_threads):
            logging.info("WebCrawler:Create and start thread number %d", idx)
            thread = threading.Thread(target=self.crawl)
            threads.append(thread)
            thread.start()

        for idx, thread in enumerate(threads):
            thread.join()
            thread_to_str = "Thread-" + str(idx)
            logging.info("WebCrawler:Main Thread Collected %s", thread_to_str)

        if self.query_found:
            print('### SUCCESS! ###\nFound query at url',
                  self.query_location, "after visiting", self.links_visited, "links")
        else:
            print('### FAILURE! ###\nCould not find query even after visiting',
                  self.links_visited, "links")


def main():
    print("Desired start url:")
    url = input()
    print("Desired query:")
    query = input()
    print("Desired cap on links to visit:")
    link_cap = int(input())
    print("Desired number of threads:")
    num_of_threads = int(input())

    web_crawler = WebCrawler(start_url=url, query=query, link_cap=link_cap, num_of_threads=num_of_threads)
    web_crawler.start()


if __name__ == '__main__':
    logging.getLogger().setLevel(logging.INFO)
    threads = list()
    main()
