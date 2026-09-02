import unittest
import tempfile
from unittest.mock import patch, MagicMock
from wikisearch.videomaker import Editor, CLIP_DURATION, FPS
from PIL import Image
from pathlib import Path

class TestEditor(unittest.TestCase):
    def test_image_with_filter_preserves_dimensions(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'test.png'
            Image.new('RGB', (100, 100), (255, 0, 0)).save(path)

            editor = Editor('test')
            result = editor.image_with_filter(path)

            self.assertEqual(result.size, (100, 100))
            self.assertEqual(result.mode, 'RGB')

    def test_image_with_filter_saves_image(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'test.png'
            Image.new('RGB', (100, 100), (255, 0, 0)).save(path)

            editor = Editor('test')
            editor.image_with_filter(path)
            saved_image = Image.open(path)

            self.assertEqual(saved_image.size, (100, 100))
            self.assertEqual(saved_image.mode, 'RGB')

    def test_image_with_filter_supports_all_colors(self):
        for color in ['none', 'blue', 'yellow', 'green']:
            with self.subTest(color=color):
                with tempfile.TemporaryDirectory() as tmp:
                    path = Path(tmp) / 'test.png'
                    Image.new('RGB', (100, 100), (255, 0, 0)).save(path)

                    editor = Editor('test')
                    with patch('wikisearch.videomaker.random.choice', return_value=color):
                        result = editor.image_with_filter(path)

                    self.assertEqual(result.size, (100, 100))
                    self.assertEqual(result.mode, 'RGB')

    @patch('wikisearch.videomaker.moviepy.ImageClip')
    def test_splice_video_returns_none_when_no_paths(self, mock_image_clip):
        editor = Editor('test')
        result = editor.splice_video([])
        self.assertIsNone(result)
        mock_image_clip.assert_not_called()

    @patch('wikisearch.videomaker.moviepy.concatenate_videoclips')
    @patch('wikisearch.videomaker.moviepy.ImageClip')
    def test_splice_video_creates_video(self, mock_image_clip, mock_concatenate):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'test.png'
            Image.new('RGB', (100, 100), (255, 0, 0)).save(path)
            editor = Editor('test')

            mock_clip = MagicMock()
            mock_video = MagicMock()
            mock_clip.with_duration.return_value = mock_clip
            mock_image_clip.return_value = mock_clip
            mock_concatenate.return_value = mock_video
            result = editor.splice_video([path])

        mock_image_clip.assert_called_once()
        mock_clip.with_duration.assert_called_once_with(CLIP_DURATION)
        mock_concatenate.assert_called_once_with([mock_clip])
        mock_video.write_videofile.assert_called_once_with(Path('test.mp4'), fps=FPS)
        mock_video.close.assert_called_once()
        mock_clip.close.assert_called_once()
        self.assertEqual(result, Path('test.mp4'))

    @patch.object(Editor, 'image_with_filter', side_effect=[Exception('bad image'), MagicMock()])
    @patch('wikisearch.videomaker.moviepy.ImageClip')
    @patch('wikisearch.videomaker.moviepy.concatenate_videoclips')
    def test_splice_video_skips_bad_image(self, mock_concatenate, mock_image_clip, mock_image_with_filter):
        editor = Editor('test')
        mock_clip = MagicMock()
        mock_video = MagicMock()

        mock_clip.with_duration.return_value = mock_clip
        mock_image_clip.return_value = mock_clip
        mock_concatenate.return_value = mock_video

        result = editor.splice_video([Path('bad.png'), Path('good.png')])

        self.assertEqual(len(editor.clips), 1)
        mock_image_clip.assert_called_once()
        mock_concatenate.assert_called_once_with([mock_clip])
        self.assertEqual(result, Path('test.mp4'))

    @patch.object(Editor, 'image_with_filter', side_effect=Exception('bad image'))
    def test_splice_video_returns_none_when_all_images_fail(self, mock_image_with_filter):
        editor = Editor('test')
        paths = [Path('bad1.png'), Path('bad2.png')]
        result = editor.splice_video(paths)

        self.assertIsNone(result)
        self.assertEqual(editor.clips, [])

    @patch('wikisearch.videomaker.random.choice', return_value='blue')
    def test_image_with_filter_changes_image(self, mock_choice):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'test.png'
            original = Image.new('RGB', (100, 100), (255, 0, 0))
            original.save(path)
            editor = Editor('test')
            result = editor.image_with_filter(path)

            self.assertNotEqual(result.getpixel((50, 50)), (255, 0, 0))

if __name__ == '__main__':
    unittest.main()