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

    # Make an initial search, if not enough screenshots try to make another search using "continue", otherwise if no search is possible then you just end
    # while True:
    # data = requests.get(...params)

    # pages = data['query']['pages']
    # process(pages)

    # if "continue" not in data:
    #     break
    # params.update(data["continue"])
    def search(self, params: dict) -> dict:
        url = self.baseUrl + "?" + urllib.parse.urlencode(params)
        request = urllib.request.Request(url, headers=self.headers)
        with urllib.request.urlopen(request) as response:
            return json.loads(response.read().decode())