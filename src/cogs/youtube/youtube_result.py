"""
Wrapper for parsing youtube web scraping results
"""
import re
from bs4 import BeautifulSoup
from typing import List
from urllib import request, parse

YT_SEARCH_URL = "https://www.youtube.com/results?search_query="
YT_WATCH_URL = "https://www.youtube.com/watch?v="

class YoutubeResult:
    def __init__(self):
        self.ids = []
        self.titles = []


    # use beautiful soup to
    # parse a youtube result page into
    # readable html, and regex out titles and urls
    def query(self, params: List[str]):
        self.ids: List[str] = []
        self.titles: List[str] = []

        html = self.parse_query(" ".join(params))
        items: BeautifulSoup = BeautifulSoup(html, "html.parser").find("ol", class_="item-section")
        ahref: BeautifulSoup = BeautifulSoup(str(items), "html.parser").find_all("a")

        title_index = 0
        ahref_index = 0

        while title_index < 5 and ahref_index < len(ahref) - 1:
            result = ahref[ahref_index]
            href = result["href"]
            title = result.get("title")

            if re.match(r'/watch\?v=(.{11})', href) and title is not None:
                title_index += 1
                self.ids.append(href.split("=")[1])
                self.titles.append("{0}. {1}".format(title_index, title))

            ahref_index += 1

        if len(self.ids) == 0:
            raise Exception("No ids found for query")

        return "{0} (type !more for related videos)".format(YT_WATCH_URL + self.ids[0])


    # retrieve a specific youtube link
    # from the previous result set
    def get_link(self, index: int) -> str:
        if len(self.ids) == 0:
            raise Exception("No youtube links available to retrieve")

        return "{0} (showing result #{1})".format(YT_WATCH_URL + self.ids[index-1], index)


    # parse the query
    @staticmethod
    def parse_query(query: str) -> str:
        query: str = parse.quote_plus(query)
        response = request.urlopen(YT_SEARCH_URL + query, timeout=1)
        html = response.read().decode()
        response.close()
        return html