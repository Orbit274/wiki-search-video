import urllib.request
import urllib.parse
import json


# IMPORTANT: keep note of potential api response errors since will be making many requests, like error code ratelimited
# Use | to combine multiple requests into 1? like titles=pageA|pageB|pageC

class WikipediaAPI:
    def __init__(self):
        self.baseUrl = 'https://en.wikipedia.org/w/api.php'
        self.headers = {'User-Agent': 'Wiki-Search-VideoBot/0.1 (github.com/Orbit274/wiki-search-video)'}

    def search(self, word: str):
        params = {'action': 'query', 'list': 'search', 'srsearch': word, 'format': 'json'}
        pass