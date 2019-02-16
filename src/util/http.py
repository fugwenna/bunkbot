import json, urllib.request
from urllib.request import HTTPError, URLError, socket
from src.models.bunk_exception import BunkException

# make a basic http call
async def http_get(self, url: str) -> json:
    try:
        return json.loads(urllib.request.urlopen(url, timeout=1).read())
    except socket.timeout:
        raise BunkException("http timeout")
    except (HTTPError, URLError) as uhe:
        raise uhe
    except Exception as e:
        raise e