import tempfile
import shutil
from playwright.sync_api import sync_playwright, Page
from pathlib import Path
from PIL import Image
from .utils import safe_filename

MAX_SCREENSHOTS = 36 # Want each screenshot to last about .12 seconds each, video should last about 3.6 seconds
TARGET_WORD_RATIO = .2
MIN_CROP_WIDTH = 300
MAX_CROP_WIDTH = 1400
# Sets css
HIGHLIGHT_CSS = '''
    html, body {
        scroll-behavior: auto !important;
    }
    term.highlight.active {
        background-color: yellow;
        padding: 2px 4px;
        color: black;
    }
'''
# Will create a treewalker, regex for all occurences of the word, go through and then wrap the word around a term element with class highlight
SEARCH_HIGHLIGHT_JS = ''' 
    (term) => {
        const escaped = RegExp.escape(term);
        const treeWalker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
        const testRegex = new RegExp(`(?<!\\\\w)${escaped}(?!\\\\w|['’])`, "i");
        const replaceRegex = new RegExp(`(?<!\\\\w)${escaped}(?!\\\\w|['’])`, "gi");
        const matches = [];
        let node;
        while (node = treeWalker.nextNode()) {
            if (testRegex.test(node.textContent)) {
                matches.push(node);
            }
        }
        for (const textNode of matches) {
            const span = document.createElement("span");
            span.innerHTML = textNode.textContent.replace(replaceRegex, '<term class="highlight">$&</term>');
            textNode.parentNode.replaceChild(span, textNode);
        }
    }
'''
SCROLL_TO_HIGHLIGHT_JS = '''
    (y) => {
        window.scrollTo({ top: y, left: 0, behavior: 'instant' });
    }
'''
CHECK_AND_LOCATE_JS = '''
    (index) => {
        const el = document.querySelectorAll('term.highlight')[index];
        if (!el) return { ok: false, reason: 'missing' };

        if (typeof el.checkVisibility === 'function' &&
            !el.checkVisibility({ opacityProperty: true, visibilityProperty: true, contentVisibilityAuto: true })) {
            return { ok: false, reason: 'not-visible' };
        }

        let node = el.parentElement;
        while (node && node !== document.body) {
            const cs = getComputedStyle(node);
            if (cs.overflow === 'hidden' || cs.overflowY === 'hidden' || cs.overflowX === 'hidden') {
                const h = parseFloat(cs.height);
                const w = parseFloat(cs.width);
                const mh = parseFloat(cs.maxHeight);
                const MIN_CLIP_SIZE = 4;
                if ((!isNaN(h) && h < MIN_CLIP_SIZE) ||
                    (!isNaN(w) && w < MIN_CLIP_SIZE) ||
                    (!isNaN(mh) && mh < MIN_CLIP_SIZE)) {
                    return { ok: false, reason: 'clipped-ancestor' };
                }
            }
            node = node.parentElement;
        }

        const rects = el.getClientRects();
        if (rects.length !== 1) {
            return { ok: false, reason: 'fragments', fragmentCount: rects.length };
        }

        const rect = rects[0];
        return { ok: true, docY: rects[0].y + window.scrollY, height: rects[0].height };
    }
'''
MEASURE_VIEWPORT_JS = '''
    (index) => {
        const el = document.querySelectorAll('term.highlight')[index];
        if (!el) return { ok: false };
        const rects = el.getClientRects();
        if (rects.length !== 1) return { ok: false };
        const r = rects[0];
        return { ok: true, x: r.x, y: r.y, width: r.width, height: r.height };
    }
'''
SET_ACTIVE_HIGHLIGHT_JS = '''
    (index) => {
        const highlight = document.querySelectorAll('term.highlight')[index];
        highlight.classList.toggle('active')
    }
'''
CLEAR_ACTIVE_HIGHLIGHT_JS = '''
    (index) => {
        const highlight = document.querySelectorAll('term.highlight')[index];
        highlight.classList.remove('active')
    }
'''

class Screenshotter:
    def __init__(self, width = 1920, height = 1080, device_scale = 3):
        self.width = width
        self.height = height
        self.device_scale = device_scale
        self.temp_dir_path = Path(tempfile.mkdtemp())
        self.screenshot_count = 0

    def process(self, json_dict: dict, term: str) -> list[Path]:
        '''Takes in a dictionary from the json file, going to find urls and then take screenshots'''
        with sync_playwright() as p:
            browser = p.chromium.launch(headless = True)
            context = browser.new_context(viewport={"width": self.width, "height": self.height}, device_scale_factor=self.device_scale)
            page = context.new_page()
            urls = self.get_urls(json_dict)
            all_outputs = []
            for url in urls:
                if self.screenshot_count >= MAX_SCREENSHOTS:
                    break
                try:
                    screenshots = self.screenshot(page, url, term, MAX_SCREENSHOTS - self.screenshot_count)
                    all_outputs.extend(screenshots)
                except Exception as e:
                    print(f'Skipping {url}: {e}')
        return all_outputs

    def get_urls(self, json_dict: dict) -> list[str]:
        if not json_dict:
            return []
        query = json_dict.get('query')
        if not query:
            return []
        pages = query.get('pages', [])
        urls = []
        for page in pages:
            url = page.get('canonicalurl')
            if url:
                urls.append(url)
        return urls

    def compute_crop(self, rect: dict) -> dict:
        crop_width = max(MIN_CROP_WIDTH, min(MAX_CROP_WIDTH, rect['width'] / TARGET_WORD_RATIO))
        crop_height = crop_width * 9 / 16
        center_x = rect['x'] + rect['width'] / 2
        center_y = rect['y'] + rect['height'] / 2
        x = max(0, min(center_x - crop_width / 2, self.width - crop_width))
        y = max(0, min(center_y - crop_height / 2, self.height - crop_height))
        return {'x': x, 'y': y, 'width': crop_width, 'height': crop_height}

    def screenshot(self, page: Page, url: str, term: str, remaining: int) -> list[Path]:
        page.goto(url, wait_until='networkidle', timeout=5000)
        page.add_style_tag(content=HIGHLIGHT_CSS)
        page.evaluate(SEARCH_HIGHLIGHT_JS, term)

        count = page.evaluate("document.querySelectorAll('term.highlight').length")
        if count == 0:
            return []
        outputs = []
        for index in range(count):
            if len(outputs) >= remaining:
                break
            page.evaluate(SET_ACTIVE_HIGHLIGHT_JS, index)

            check = page.evaluate(CHECK_AND_LOCATE_JS, index)
            if not check['ok']:
                continue

            target_scroll_y = max(0, check['docY'] - (self.height - check['height']) / 2)
            page.evaluate(SCROLL_TO_HIGHLIGHT_JS, target_scroll_y)
            rect = page.evaluate(MEASURE_VIEWPORT_JS, index)
            if (not rect['ok'] or rect['y'] < 0 or rect['y'] + rect['height'] > self.height
                    or rect['x'] < 0 or rect['x'] + rect['width'] > self.width):
                continue

            clip = self.compute_crop(rect)
            path = self.temp_dir_path / f'{safe_filename(term)}_{self.screenshot_count:03d}.png'
            try:
                page.screenshot(path=path, clip=clip)
                img = Image.open(path)
                img = img.resize((self.width, self.height), Image.Resampling.LANCZOS)
                img.save(path)
                print(f'Screenshot {self.screenshot_count} taken at {url}')
            except Exception as e:
                print(f'Failed to take a screenshot: {e}')
                continue
            finally:
                page.evaluate(CLEAR_ACTIVE_HIGHLIGHT_JS, index)

            self.screenshot_count += 1
            outputs.append(path)
        return outputs

    def remove_temporary(self) -> None:
        '''Removes temporary screenshots'''
        # Uncomment during final phases, keep commented during photo analysis/debugging
        # shutil.rmtree(self.temp_dir_path)
        return