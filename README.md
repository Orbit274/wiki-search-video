## Logic
Use MediaWiki API to find Wikipedia pages with the desired search term <br>
Use Playwright to load the page and take screenshots <br>
Use imageio-ffmpeg to splice together screenshots and create a video file <br>

## Ways to use
Command line interaction, requires running via terminal <br>
Simple gui with tkinter, can run via terminal or vscode "run" <br>
Simple local web page with streamlit, requires running via terminal <br>

## Usage
Command line: <br>
Installation <br>
```bash
cd wiki-search-video
pip install .
playwright install chromium
```
Running <br>
```bash
python cli.py -- term "help"
python gui_tkinter.py
streamlit run gui_streamlit.py
```