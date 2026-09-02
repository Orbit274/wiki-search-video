import unittest
import urllib.error
from wikisearch.api import WikipediaAPI
from unittest.mock import patch, MagicMock

class TestWikipediaAPI(unittest.TestCase):
    def test_get_params(self):
        api = WikipediaAPI()
        params = api.get_params('chill')
        self.assertEqual(params['gsrsearch'], '"chill"')
        self.assertEqual(params['format'], 'json')

    @patch('wikisearch.api.urllib.request.urlopen')
    def test_request_success(self, mock_urlopen):
        mock_response = MagicMock()
        mock_response.read.return_value = b'{"query": {"pages": []}}'
        mock_urlopen.return_value.__enter__.return_value = mock_response
        api = WikipediaAPI()
        result = api.request({})
        self.assertEqual(result, {"query": {"pages": []}})

    @patch('wikisearch.api.urllib.request.urlopen')
    def test_request_raises_on_error(self, mock):
        mock.side_effect = urllib.error.HTTPError(url='x', code=429, msg='Too many requests', hdrs=None, fp=None)
        api = WikipediaAPI()
        with self.assertRaises(RuntimeError):
            api.request({})

    @patch('wikisearch.api.urllib.request.urlopen')
    def test_request_raises_on_url_error(self, mock_urlopen):
        mock_urlopen.side_effect = urllib.error.URLError("Connection failed")
        api = WikipediaAPI()
        with self.assertRaises(RuntimeError):
            api.request({})

    @patch('wikisearch.api.urllib.request.urlopen')
    def test_request_raises_on_invalid_json(self, mock_urlopen):
        mock_response = MagicMock()
        mock_response.read.return_value = b'not valid json'
        mock_urlopen.return_value.__enter__.return_value = mock_response
        api = WikipediaAPI()
        with self.assertRaises(RuntimeError):
            api.request({})

    @patch('wikisearch.api.urllib.request.urlopen')
    def test_request_raises_on_api_error(self, mock_urlopen):
        mock_response = MagicMock()
        mock_response.read.return_value = (b'{"error": {"code": "ratelimited", "info": "Too many requests"}}')
        mock_urlopen.return_value.__enter__.return_value = mock_response
        api = WikipediaAPI()
        with self.assertRaises(RuntimeError):
            api.request({})

if __name__ == '__main__':
    unittest.main()