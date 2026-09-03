import moviepy
import random
import numpy
from pathlib import Path
from PIL import Image, ImageFilter, ImageEnhance
from .utils import safe_filename

CLIP_DURATION = .1
FPS = 30

class Editor:
    def __init__(self, term):
        self.term = term
        self.clips = []

    def splice_video(self, paths: list[Path]) -> Path | None:
        # Take the paths, put a filter on them, create clips from moviepy, append to a clips array, may need to turn PIL obj into numpy array
        # then create a video by concatenating clips, then write video file
        for path in paths:
            try:
                img = self.image_with_filter(path)
                frame = numpy.array(img)
                clip = moviepy.ImageClip(frame).with_duration(CLIP_DURATION)
                self.clips.append(clip)
            except Exception as e:
                print(f'Skipping {path}: {e}')
        if not self.clips:
            print('No clips')
            return None
        video = moviepy.concatenate_videoclips(self.clips)
        output = Path(f'{safe_filename(self.term)}.mp4')
        video.write_videofile(output, fps=FPS)
        video.close()
        for clip in self.clips:
            clip.close()
        return output

    def image_with_filter(self, image_path: Path) -> Image.Image:
        img = Image.open(image_path).convert('RGB')
        color_name = random.choice(['none', 'blue', 'yellow', 'green'])
        match color_name:
            case 'blue':
                overlay = Image.new('RGB', img.size, (0, 180, 255))
            case 'yellow':
                overlay = Image.new('RGB', img.size, (255, 220, 0))
            case 'green':
                overlay = Image.new('RGB', img.size, (50, 200, 50))
            case 'none':
                overlay = None

        if overlay is not None:
            img = Image.blend(img, overlay, .25)
        img = ImageEnhance.Contrast(img).enhance(1.4)
        img = img.filter(ImageFilter.GaussianBlur(.5))

        arr = numpy.array(img)
        noise = numpy.random.normal(0, 12, arr.shape)
        arr = numpy.clip(arr + noise, 0, 255).astype(numpy.uint8)
        img = Image.fromarray(arr)
        
        img.save(image_path)
        return img