import tempfile
from playwright.sync_api import sync_playwright
from pathlib import Path

# MAX_SCREENSHOTS = 30 # Want each screenshot to last about .12 seconds each, video should last about 3.6 seconds
# # Sets css
# HIGHLIGHT_CSS = '''
#     term.highlight {
#         background-color: yellow;
#         padding: 2px 4px;
#     }
# '''
# # Will create a treewalker, regex for all occurences of the word, go through and then wrap the word around a term element with class highlight
# SEARCH_HIGHLIGHT_JS = ''' 
#     (term) => {
#         const treeWalker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
#         const regex = new RegExp(`\\\\b${term}\\\\b`, "gi");
#         let node;
#         while (node = walker.nextNode()) {
#             const text = node.textContent;
#             if (!regex.test(text)) {
#                 continue;
#             }
#             const span = document.createElement("span");
#             span.innerHTML = text.replace(regex, '<term class="highlight">$&</mark>');
#             node.parentNode.replaceChild(span, node);
#         }
#     }
# '''
# # Selects all highlights, converts the nodelist into an array, loops through each element,
# # get the size and position of element relative to viewport, can use to get bounding box
# # returning a js object that stores the absolute position of top left of each boudning box
# BOUNDING_JS = '''
#     () => {
#         return [...document.querySelectorAll('mark.highlight')].map(highlighted => {
#             const rect = highlighted.getBoundingClientRect();
#             return {
#                 x: rect.x + window.scrollX,
#                 y: rect.y + window.scrollY,
#                 width: rect.width,
#                 height: rect.height
#             };
#         });
#     }
# '''

class Screenshotter:
    def __init__(self, width = 1920, height = 1080):
        self.width = width
        self.height = height
        self.temp_dir_path = Path(tempfile.mkdtemp())

    def process(self, json, term):
        '''Takes in a dictionary from the json file, going to find urls and then take screenshots'''
        with sync_playwright() as p:
            browser = p.chromium.launch(headless = True)
            context = browser.new_context(viewport={"width": self.width, "height": self.height})
            page = context.new_page()

    # def screenshot(self, page, url, term):
    #     '''Goes to page, injects css for highlighting, highlights every single term, finds their bounding boxes, takes screenshots'''
    #     page.goto(url)
    #     page.add_style_tag(content = HIGHLIGHT_CSS)
    #     page.evaluate(SEARCH_HIGHLIGHT_JS, term)
    #     boxes = page.evaluate(BOUNDING_JS)
    #     if not boxes:
    #         return None;

    #     padding = 40
    #     outputs = []
    #     for i, box in enumerate(boxes):
    #         clip = {
    #             'x': max(0, box['x'] - padding),
    #             'y': max(0, box['y'] - padding),
    #             'width': box['width'] + padding * 2,
    #             'height': box['height'] + padding * 2,
    #         }
    #         path = self.temp_dir_path / f'{term}_{i}.png'
    #         page.screenshot(path = path, clip = clip)
    #         outputs.append(path)
    #     return outputs