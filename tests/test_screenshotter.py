import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock
from PIL import Image
from wikisearch.screenshotter import (
    Screenshotter,
    MAX_CROP_WIDTH,
    MIN_CROP_WIDTH,
    TARGET_WORD_RATIO,
    HIGHLIGHT_CSS,
    MAX_SCREENSHOTS,
    SCROLL_TO_HIGHLIGHT_JS
)

class TestScreenshotter(unittest.TestCase):
    def test_compute_crop(self):
        screenshotter = Screenshotter(width=2000, height=2000)
        box = {'x': 500, 'y': 500, 'width': 100, 'height': 40}
        clip = screenshotter.compute_crop(box)
        expected_width = 100 / TARGET_WORD_RATIO
        expected_height = expected_width * 9 / 16
        expected_x = 500 + 100 / 2 - expected_width / 2
        expected_y = 500 + 40 / 2 - expected_height / 2
        self.assertEqual(clip['width'], expected_width)
        self.assertEqual(clip['height'], expected_height)
        self.assertEqual(clip['x'], expected_x)
        self.assertEqual(clip['y'], expected_y)

    def test_compute_crop_clamps_to_max_width(self):
        screenshotter = Screenshotter(width=10000, height=10000)
        box = {'x': 100, 'y': 100, 'width': 5000, 'height': 40}
        clip = screenshotter.compute_crop(box)
        self.assertEqual(clip['width'], MAX_CROP_WIDTH)
        self.assertEqual(clip['height'], MAX_CROP_WIDTH * 9 / 16)

    def test_compute_crop_clamps_to_min_width(self):
        screenshotter = Screenshotter(width=2000, height=2000)
        box = {'x': 100, 'y': 100, 'width': 10, 'height': 20}
        clip = screenshotter.compute_crop(box)
        self.assertEqual(clip['width'], MIN_CROP_WIDTH)
        self.assertEqual(clip['height'], MIN_CROP_WIDTH * 9 / 16)

    def test_compute_crop_clamps_left_edge(self):
        screenshotter = Screenshotter(width=2000, height=2000)
        box = {'x': 0, 'y': 500, 'width': 100, 'height': 40}
        clip = screenshotter.compute_crop(box)
        self.assertEqual(clip['x'], 0)

    def test_compute_crop_clamps_right_edge(self):
        screenshotter = Screenshotter(width=2000, height=2000)
        box = {'x': 1900, 'y': 500, 'width': 100, 'height': 40}
        clip = screenshotter.compute_crop(box)
        expected_x = screenshotter.width- clip['width']
        self.assertEqual(clip['x'], expected_x)

    def test_compute_crop_clamps_bottom_edge(self):
        screenshotter = Screenshotter(width=2000, height=2000)
        box = {'x': 500, 'y': 1900, 'width': 100, 'height': 40}
        clip = screenshotter.compute_crop(box)
        expected_y = screenshotter.height - clip['height']
        self.assertEqual(clip['y'], expected_y)

    def test_crop_is_16_by_9(self):
        screenshotter = Screenshotter(width=2000, height=2000)
        box = {'x': 500, 'y': 500, 'width': 100, 'height': 40}
        clip = screenshotter.compute_crop(box)
        self.assertAlmostEqual(clip['width'] / clip['height'], 16 / 9)

    def test_get_urls_returns_canonical_urls(self):
        screenshotter = Screenshotter()
        data = {
            'query': {
                'pages': [
                    {
                        'title': 'Python',
                        'canonicalurl': 'https://en.wikipedia.org/wiki/Python',
                    },
                    {
                        'title': 'Java',
                        'canonicalurl': 'https://en.wikipedia.org/wiki/Java',
                    },
                ]
            }
        }
        result = screenshotter.get_urls(data)
        self.assertEqual(result, ['https://en.wikipedia.org/wiki/Python', 'https://en.wikipedia.org/wiki/Java'])

    def test_get_urls_returns_empty_list_for_empty_response(self):
        screenshotter = Screenshotter()
        self.assertEqual(screenshotter.get_urls({}), [])

    def test_get_urls_returns_empty_list_when_pages_missing(self):
        screenshotter = Screenshotter()
        data = {'query': {}}
        self.assertEqual(screenshotter.get_urls(data), [])

    def test_get_urls_ignores_pages_without_canonical_url(self):
        screenshotter = Screenshotter()
        data = {
            'query': {
                'pages': [
                    {
                        'title': 'Python',
                        'canonicalurl': 'https://en.wikipedia.org/wiki/Python',
                    },
                    {
                        'title': 'No URL',
                    },
                    {
                        'title': 'Another',
                        'canonicalurl': None,
                    },
                ]
            }
        }
        result = screenshotter.get_urls(data)
        self.assertEqual(result, ['https://en.wikipedia.org/wiki/Python'])

    def test_screenshot_returns_empty_list_when_no_highlights(self):
        screenshotter = Screenshotter()
        page = MagicMock()
        page.evaluate.side_effect = [None, 0]
        result = screenshotter.screenshot(page, 'https://example.com', 'python', remaining=30)
        self.assertEqual(result, [])
        page.goto.assert_called_once_with('https://example.com', wait_until='networkidle', timeout=5000)
        page.add_style_tag.assert_called_once_with(content=HIGHLIGHT_CSS)
        page.screenshot.assert_not_called()

    def test_screenshot_takes_screenshot_for_each_highlight(self):
        screenshotter = Screenshotter()
        page = MagicMock()
        boxes = [
            {
                'ok': True,
                'x': 500,
                'y': 500,
                'width': 100,
                'height': 40,
            },
            {
                'ok': True,
                'x': 800,
                'y': 700,
                'width': 100,
                'height': 40,
            },
        ]
        page.evaluate.side_effect = [None, 2, None, {'ok': True, 'docY': 500, 'height': 40}, None, boxes[0], None, None, {'ok': True, 'docY': 700, 'height': 40}, None,  boxes[1], None]

        def fake_screenshot(path, clip):
            image = Image.new('RGB', (500, 500), 'white')
            image.save(path)

        page.screenshot.side_effect = fake_screenshot
        result = screenshotter.screenshot(page, 'https://example.com', 'python', remaining=30)
        self.assertEqual(len(result), 2)
        self.assertEqual(screenshotter.screenshot_count, 2)
        self.assertEqual(page.screenshot.call_count, 2)
        for path in result:
            self.assertTrue(path.exists())

    def test_screenshot_respects_remaining_limit(self):
        screenshotter = Screenshotter()
        page = MagicMock()
        boxes = [
            {
                'ok': True,
                'x': 500,
                'y': 500,
                'width': 100,
                'height': 40,
            },
            {
                'ok': True,
                'x': 800,
                'y': 700,
                'width': 100,
                'height': 40,
            },
            {
                'ok': True,
                'x': 1000,
                'y': 900,
                'width': 100,
                'height': 40,
            },
        ]
        page.evaluate.side_effect = [None, 3, None, {'ok': True, 'docY': 500, 'height': 40}, None, boxes[0], None, None, {'ok': True, 'docY': 700, 'height': 40}, None, boxes[1], None]

        def fake_screenshot(path, clip):
            image = Image.new('RGB', (500, 500), 'white')
            image.save(path)

        page.screenshot.side_effect = fake_screenshot
        result = screenshotter.screenshot(page, 'https://example.com', 'python', remaining=2)
        self.assertEqual(len(result), 2)
        self.assertEqual(screenshotter.screenshot_count, 2)
        self.assertEqual(page.screenshot.call_count, 2)

    def test_screenshot_passes_correct_clip_to_playwright(self):
        screenshotter = Screenshotter(width=2000, height=2000)
        page = MagicMock()
        box = {
            'ok': True,
            'x': 500,
            'y': 500,
            'width': 100,
            'height': 40,
        }
        page.evaluate.side_effect = [None, 1, None, {'ok': True, 'docY': 500, 'height': 40}, None, box, None]

        def fake_screenshot(path, clip):
            image = Image.new('RGB', (500, 500), 'white')
            image.save(path)

        page.screenshot.side_effect = fake_screenshot
        screenshotter.screenshot(page, 'https://example.com','python', remaining=30)
        expected_clip = screenshotter.compute_crop(box)
        _, kwargs = page.screenshot.call_args
        self.assertEqual(kwargs['clip'], expected_clip)

    @patch('wikisearch.screenshotter.sync_playwright')
    def test_process_collects_screenshots_from_urls(self, mock_sync_playwright):
        screenshotter = Screenshotter()
        playwright = MagicMock()
        browser = MagicMock()
        context = MagicMock()
        page = MagicMock()

        mock_sync_playwright.return_value.__enter__.return_value = playwright
        playwright.chromium.launch.return_value = browser
        browser.new_context.return_value = context
        context.new_page.return_value = page

        screenshots = [Path('screenshot1.png'), Path('screenshot2.png')]
        screenshotter.screenshot = MagicMock(return_value=screenshots)

        data = {
            'query': {
                'pages': [
                    {
                        'canonicalurl': 'https://example.com/one',
                    },
                    {
                        'canonicalurl': 'https://example.com/two',
                    },
                ]
            }
        }

        result = screenshotter.process(data, 'python')
        self.assertEqual(result, screenshots + screenshots)
        self.assertEqual(screenshotter.screenshot.call_count, 2)
        screenshotter.screenshot.assert_any_call(page, 'https://example.com/one', 'python', MAX_SCREENSHOTS)
        screenshotter.screenshot.assert_any_call(page, 'https://example.com/two', 'python', MAX_SCREENSHOTS)

    @patch('wikisearch.screenshotter.sync_playwright')
    def test_process_does_not_exceed_max_screenshots(self, mock_sync_playwright):
        screenshotter = Screenshotter()
        screenshotter.screenshot_count = MAX_SCREENSHOTS
        playwright = MagicMock()
        browser = MagicMock()
        context = MagicMock()
        page = MagicMock()

        mock_sync_playwright.return_value.__enter__.return_value = playwright
        playwright.chromium.launch.return_value = browser
        browser.new_context.return_value = context
        context.new_page.return_value = page

        screenshotter.screenshot = MagicMock()

        data = {
            'query': {
                'pages': [
                    {
                        'canonicalurl': 'https://example.com',
                    },
                ]
            }
        }

        result = screenshotter.process(data, 'python')
        self.assertEqual(result, [])
        screenshotter.screenshot.assert_not_called()

    def test_screenshot_scrolls_to_crop(self):
        screenshotter = Screenshotter(width=2000, height=2000)
        page = MagicMock()
        box = {
            'ok': True,
            'x': 500,
            'y': 500,
            'width': 100,
            'height': 40,
        }

        page.evaluate.side_effect = [None, 1, None, {'ok': True, 'docY': 2000, 'height': 40}, None, box, None]
        def fake_screenshot(path, clip):
            image = Image.new('RGB', (500, 500), 'white')
            image.save(path)

        page.screenshot.side_effect = fake_screenshot
        screenshotter.screenshot(page, 'https://example.com', 'python', remaining=30)
        expected_scroll_y = max(0, 2000 - (screenshotter.height - 40) / 2)
        page.evaluate.assert_any_call(SCROLL_TO_HIGHLIGHT_JS, expected_scroll_y)

if __name__ == '__main__':
    unittest.main()