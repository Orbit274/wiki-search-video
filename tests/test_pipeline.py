import unittest
from unittest.mock import patch, MagicMock
from wikisearch.pipeline import generate_video
from pathlib import Path

class TestGeneratePipeline(unittest.TestCase):
    @patch('wikisearch.pipeline.Editor')
    @patch('wikisearch.pipeline.Screenshotter')
    @patch('wikisearch.pipeline.WikipediaAPI')
    def test_generate_video_success(self, mock_api_class, mock_screenshotter_class, mock_editor_class):
        mock_api = mock_api_class.return_value
        mock_screenshotter = mock_screenshotter_class.return_value
        mock_editor = mock_editor_class.return_value

        mock_api.get_params.return_value = {'action': 'query', 'generator': 'search'}
        mock_api.request.return_value = {
            'query': {
                'pages': [
                    {'canonicalurl': 'https://example.com'}
                ]
            }
        }

        screenshot = Path('screenshot.png')
        output = Path('test.mp4')

        mock_screenshotter.process.return_value = [screenshot]
        mock_editor.splice_video.return_value = output
        result = generate_video('python')

        self.assertEqual(result, output)
        mock_api.get_params.assert_called_once_with('python')
        mock_api.request.assert_called_once()
        mock_screenshotter.process.assert_called_once()
        mock_editor.splice_video.assert_called_once_with([screenshot])

        mock_screenshotter.remove_temporary.assert_called_once()

    @patch('wikisearch.pipeline.Editor')
    @patch('wikisearch.pipeline.Screenshotter')
    @patch('wikisearch.pipeline.WikipediaAPI')
    def test_generate_video_returns_none_when_no_screenshots(self, mock_api_class, mock_screenshotter_class, mock_editor_class):
        mock_api = mock_api_class.return_value
        mock_screenshotter = mock_screenshotter_class.return_value

        mock_api.get_params.return_value = {'test': 'params'}
        mock_api.request.return_value = {
            'query': {
                'pages': []
            }
        }
        mock_screenshotter.process.return_value = []

        result = generate_video('python')

        self.assertIsNone(result)
        mock_screenshotter.remove_temporary.assert_called_once()
        mock_editor_class.return_value.splice_video.assert_not_called()

    @patch('wikisearch.pipeline.time.sleep')
    @patch('wikisearch.pipeline.Editor')
    @patch('wikisearch.pipeline.Screenshotter')
    @patch('wikisearch.pipeline.WikipediaAPI')
    def test_generate_video_retries_api_request(self, mock_api_class, mock_screenshotter_class, mock_editor_class, mock_sleep):
        mock_api = mock_api_class.return_value
        mock_screenshotter = mock_screenshotter_class.return_value
        mock_editor = mock_editor_class.return_value

        mock_api.get_params.return_value = {'test': 'params'}
        mock_api.request.side_effect = [
            RuntimeError('temporary failure'),
            {'query': {'pages': []}},
        ]
        mock_screenshotter.process.return_value = []

        result = generate_video('python')

        self.assertIsNone(result)
        self.assertEqual(mock_api.request.call_count, 2)
        mock_sleep.assert_called_once_with(1)

    @patch('wikisearch.pipeline.time.sleep')
    @patch('wikisearch.pipeline.WikipediaAPI')
    def test_generate_video_raises_after_max_api_attempts(self, mock_api_class, mock_sleep):
        mock_api = mock_api_class.return_value
        
        mock_api.get_params.return_value = {'test': 'params'}
        mock_api.request.side_effect = RuntimeError('Wikipedia is down')

        with self.assertRaises(RuntimeError) as context:
            generate_video('python')

        self.assertIn(
            'API request failed after 3 attempts',
            str(context.exception)
        )

        self.assertEqual(mock_api.request.call_count, 3)
        self.assertEqual(mock_sleep.call_count, 2)

    @patch('wikisearch.pipeline.Editor')
    @patch('wikisearch.pipeline.Screenshotter')
    @patch('wikisearch.pipeline.WikipediaAPI')
    def test_generate_video_follows_api_continuation(self, mock_api_class, mock_screenshotter_class, mock_editor_class):
        mock_api = mock_api_class.return_value
        mock_screenshotter = mock_screenshotter_class.return_value
        mock_editor = mock_editor_class.return_value

        initial_params = {'search': 'python'}

        mock_api.get_params.return_value = initial_params
        mock_api.request.side_effect = [
            {
                'query': {
                    'pages': [
                        {'canonicalurl': 'https://example.com/1'}
                    ]
                },
                'continue': {
                    'gsroffset': 20
                }
            },
            {
                'query': {
                    'pages': [
                        {'canonicalurl': 'https://example.com/2'}
                    ]
                }
            }
        ]

        first_screenshot = Path('one.png')
        second_screenshot = Path('two.png')

        mock_screenshotter.process.side_effect = [
            [first_screenshot],
            [second_screenshot],
        ]

        output = Path('test.mp4')
        mock_editor.splice_video.return_value = output

        result = generate_video('python')

        self.assertEqual(result, output)

        self.assertEqual(mock_api.request.call_count, 2)
        self.assertEqual(mock_screenshotter.process.call_count, 2)

        mock_editor.splice_video.assert_called_once_with([first_screenshot, second_screenshot])

    @patch('wikisearch.pipeline.Editor')
    @patch('wikisearch.pipeline.Screenshotter')
    @patch('wikisearch.pipeline.WikipediaAPI')
    def test_generate_video_cleans_up_when_video_creation_fails(self, mock_api_class, mock_screenshotter_class, mock_editor_class):
        mock_api = mock_api_class.return_value
        mock_screenshotter = mock_screenshotter_class.return_value
        mock_editor = mock_editor_class.return_value

        mock_api.get_params.return_value = {'test': 'params'}
        mock_api.request.return_value = {
            'query': {
                'pages': [
                    {'canonicalurl': 'https://example.com'}
                ]
            }
        }

        screenshot = Path('screenshot.png')
        mock_screenshotter.process.return_value = [screenshot]
        mock_editor.splice_video.side_effect = RuntimeError('MoviePy failed')

        with self.assertRaises(RuntimeError):
            generate_video('python')

        mock_screenshotter.remove_temporary.assert_called_once()

if __name__ == '__main__':
    unittest.main()