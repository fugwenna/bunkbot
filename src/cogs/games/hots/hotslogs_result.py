from bs4 import BeautifulSoup
from urllib import request, parse
from src.util.bunk_exception import BunkException
from .hots_exception import HotsException

HOTS_PLAYER_NAME_URL: str = "https://www.hotslogs.com/PlayerSearch?Name="
HOTS_PLAYER_ID_URL: str = "https://www.hotslogs.com/Player/Profile?PlayerID="

PLAYER_MAIN_GRID_ID: str = "ctl00_MainContent_RadGridGeneralInformation"

class HotslogsResult:
    # scrape the player id site
    # and find the primary info table
    def get_player_by_id(self, pid: int, table: str = None):
        # no table passed, assume
        # an id lookup
        if table is None:
            html = self.scrape(HOTS_PLAYER_ID_URL + str(pid))
            table = BeautifulSoup(html, "html.parser").find("table", class_="rgMasterTable", id=PLAYER_MAIN_GRID_ID)

        tbody = BeautifulSoup(str(table), "html.parser").find_all("tbody")
        trows = BeautifulSoup(str(tbody), "html.parser").find_all("tr")

        if len(trows) == 0:
            raise BunkException("Error parsing information for player {}".format(str(pid)))

        for ind in range(0, len(trows)-1):
            tds = BeautifulSoup(str(trows[ind]), "html.parser").find_all("td")

            if ind <= 3:
                league_name = tds[0].contents[0]
                league = tds[1].find("span").contents[0].split(" ")[0]

                print("{0}: {1}".format(league_name, league))


    # search by name
    def get_player_by_name(self, name: str):
        html = self.scrape(HOTS_PLAYER_NAME_URL + str)

        # if there was one result, update with
        # the single player result
        table = BeautifulSoup(html, "html.parser").find("table", class_="rgMasterTable")
        if table is not None:
            self.get_player_by_id(-1, table)
        else:
            raise HotsException(HOTS_PLAYER_NAME_URL + str)


    # scrape the hotslogs url passed
    # and return the HTML for bs4
    @staticmethod
    def scrape(url) -> str:
        response = request.urlopen(url)
        html = response.read().decode()
        response.close()
        return html