import time
import logging
from .api import WikipediaAPI
from .screenshotter import Screenshotter, MAX_SCREENSHOTS
from .videomaker import Editor
from pathlib import Path

MAX_API_ATTEMPTS = 3

logger = logging.getLogger(__name__)

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
            logger.warning('API request failed (%s/%s): %s', failure_count, MAX_API_ATTEMPTS, e)
            if failure_count >= MAX_API_ATTEMPTS:
                raise RuntimeError(f'API request failed after {MAX_API_ATTEMPTS} attempts') from e
            time.sleep(1)
            continue

        screenshots = screenshotter.process(data, term)
        all_screenshots.extend(screenshots)

        if len(all_screenshots) >= MAX_SCREENSHOTS:
            break
        if 'continue' not in data:
            logger.info('No more occurrences of %s', term)
            break
        params.update(data['continue'])

    if not all_screenshots:
        screenshotter.remove_temporary()
        return None

    try:
        logger.info('Creating video now')
        return editor.splice_video(all_screenshots)
    except Exception as e:
        logger.info('Video production error: %s', e)
    finally:
        screenshotter.remove_temporary()