import urllib.request
import urllib.parse
import json

class WikipediaAPI:
    def __init__(self):
        self.base_url = 'https://en.wikipedia.org/w/api.php'
        self.headers = {'User-Agent': 'Wiki-Search-VideoBot/0.1 (github.com/Orbit274/wiki-search-video)'}

    def get_params(self, word: str) -> dict:
        return {'action': 'query', 'generator': 'search', 'gsrsearch': f'"{word}"', 'gsrlimit': 20, 'prop': 'info', 'inprop': 'url', 'format': 'json', 'formatversion': 2}

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