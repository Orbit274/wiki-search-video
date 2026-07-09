import moviepy
import PIL
import random
import imageio_ffmpeg
import numpy
from pathlib import Path

ffmpeg_path = imageio_ffmpeg.get_ffmpeg_exe()
if not ffmpeg_path:
    exit()

class Editor:
    def __init__(self, term):
        self.term = term
        self.clips = []

    def spliceVideo(self, paths: list[Path]) -> None:
        # Take the paths, put a filter on them, create clips from moviepy, append to a clips array, may need to turn PIL obj into numpy array
        # then create a video by concatenating clips, then write video file
        for path in paths:
            img = self.imageWithFilter(path)
            frame = numpy.array(img)
            clip = moviepy.ImageClip(frame).with_duration(.12)
            self.clips.append(clip)
        video = moviepy.concatenate_videoclips(self.clips, method="compose")
        video.write_videofile(f'{self.term}.mp4', fps=30)
        video.close()
        for clip in self.clips:
            clip.close()

    def imageWithFilter(self, image_path: Path) -> PIL.Image:
        img = PIL.Image.open(image_path).convert('RGB')
        color = random.choice(['none', 'blue', 'yellow', 'green'])
        match color:
            case 'blue':
                color = PIL.Image.new('RGB', img.size, (0, 180, 255))
            case 'yellow':
                color = PIL.Image.new('RGB', img.size, (255, 220, 0))
            case 'green':
                color = PIL.Image.new('RGB', img.size, (50, 200, 50))
            case 'none':
                color = None

        if color is not None:
            img = PIL.Image.blend(img, color, .25)
        img = PIL.ImageEnhance.Contrast(img).enhance(1.4)
        img = img.filter(PIL.ImageFilter.GaussianBlur(.5))

        arr = numpy.array(img)
        noise = numpy.random.normal(0, 12, arr.shape)
        arr = numpy.clip(arr + noise, 0, 255).astype(numpy.uint8)
        img = PIL.Image.fromarray(arr)
        
        img.save(image_path)
        return img