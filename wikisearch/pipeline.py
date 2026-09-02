import time
from .api import WikipediaAPI
from .screenshotter import Screenshotter, MAX_SCREENSHOTS
from .videomaker import Editor
from pathlib import Path

MAX_API_ATTEMPTS = 3

def generate_video(term: str) -> Path | None:
    api = WikipediaAPI()
    screenshotter = Screenshotter()
    editor = Editor(term)
    failure_count = 0

    params = api.get_params(term)
    all_screenshots = []

    while True:
        try:
            data = api.request(params)
        except RuntimeError as e:
            failure_count += 1
            print(f'API request failed ({failure_count}/{MAX_API_ATTEMPTS}): {e}')
            if failure_count >= MAX_API_ATTEMPTS:
                raise RuntimeError(f'API request failed after {MAX_API_ATTEMPTS} attempts') from e
            time.sleep(1)
            continue

        screenshots = screenshotter.process(data, term)
        all_screenshots.extend(screenshots)

        if len(all_screenshots) >= MAX_SCREENSHOTS:
            break
        if 'continue' not in data:
            print(f'No more occurrences of {term}')
            break
        params.update(data['continue'])

    if not all_screenshots:
        screenshotter.remove_temporary()
        return None

    try:
        return editor.splice_video(all_screenshots)
    finally:
        screenshotter.remove_temporary()