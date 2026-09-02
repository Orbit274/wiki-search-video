import urllib.request
import urllib.parse
import json


# IMPORTANT: keep note of potential api response errors since will be making many requests, like error code ratelimited
# Use | to combine multiple requests into 1? like titles=pageA|pageB|pageC

class WikipediaAPI:
    def __init__(self):
        self.baseUrl = 'https://en.wikipedia.org/w/api.php'
        self.headers = {'User-Agent': 'Wiki-Search-VideoBot/0.1 (github.com/Orbit274/wiki-search-video)'}

    def baseParams(self, word: str) -> dict:
        return {'action': 'query', 'generator': 'search', 'gsrsearch': f'insource:"{word}"', 'gsrlimit': 20, 'prop': 'info', 'inprop': 'url', 'format': 'json', 'formatversion': 2, 'pretty': 1}

    def request(self, params: dict) -> dict:
        url = self.base_url + "?" + urllib.parse.urlencode(params)
        request = urllib.request.Request(url, headers=self.headers)

        try:
            with urllib.request.urlopen(request) as response:
                data = json.loads(response.read().decode())
        except urllib.error.HTTPError as e:
            raise RuntimeError(f'Wikipedia has returned HTTP {e.code}') from e
        except urllib.error.URLError as e:
            raise RuntimeError(f'Connection failed: {e.reason}') from e
        except json.JSONDecodeError as e:
            raise RuntimeError('Wikipedia has invalid JSON') from e
        except Exception as e:
            raise RuntimeError(f'Unknown error: {e}') from e

        if 'error' in data:
            raise RuntimeError(data['error'])
        return data