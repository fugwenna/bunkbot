import json, urllib.request
from urllib.request import HTTPError, URLError, socket

from .bunk_exception import BunkException

# make a basic http call
async def http_get(url: str) -> json:
    try:
        http_result = urllib.request.urlopen(url, timeout=1).read()
        return json.loads(http_result)
    except socket.timeout:
        raise BunkException("http timeout")
    except (HTTPError, URLError) as uhe:
        print(uhe)
        raise uhe
    except Exception as e:
        raise e
