from googleapiclient.discovery import build
from typing import List

from ..core.bunk_exception import BunkException
from ..etc.config_service import ConfigService

YT_SEARCH_URL = "https://googleapis.com/youtube/v3/search"
YT_WATCH_URL = "https://www.youtube.com/watch?v="

class YoutubeResult:
    """
    A stateful object that will wrap google (youtube) api requests into 
    a clean format for a youtube cog to render links
    """
    def __init__(self):
        self.ids = []
        self.titles = []
        self.qualified_query: str = None
        self.config: ConfigService = ConfigService()
        self.yt_service = build("youtube", "v3", developerKey=self.config.youtube_api_key)


    def query(self, params: List[str]):
        """
        Description
        ------------
            Use the v3 youtube API to perform a basic youtube data search

        Parameters
        -----------
        params: List[str]
            Parameters passed from the youtube cog ctx object 
        """
        self.ids: List[str] = []
        self.titles: List[str] = []
        self.qualified_query = "{0}{1}".format(YT_WATCH_URL, " ".join(params))

        req = self.yt_service.search().list(q=" ".join(params), part="snippet", type="video")
        result = req.execute()

        index = 0
        for r in result["items"]:
            self.ids.append(r["id"]["videoId"])
            self.titles.append("{0}. {1}".format(index + 1, r["snippet"]["title"]))
            index+=1

        if len(self.ids) == 0:
            raise BunkException("No ids found for query")

        return "{0} (type !more for related videos)".format(YT_WATCH_URL + self.ids[0])


    def get_link(self, index: int) -> str:
        """
        Description
        ------------
        Retrieve a specific youtube link from the previous result set

        Parameters
        -----------
        index: int
            Index (+1) of the item in the more list
        """
        if len(self.ids) == 0:
            raise Exception("No youtube links available to retrieve")

        return "{0} (showing result #{1})".format(YT_WATCH_URL + self.ids[index-1], index)
