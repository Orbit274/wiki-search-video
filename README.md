## Logic
Use MediaWiki API to find Wikipedia pages with the desired search term <br>
Use Playwright to load the page and take screenshots <br>
Use imageio-ffmpeg to splice together screenshots and create a video file <br>

## Ways to use
Command line interaction, requires running via terminal <br>
Simple gui with tkinter, can run via terminal or vscode "run" <br>
Simple local web page with streamlit, requires running via terminal <br>

## Usage
First clone the repository and navigate to the project directory
```bash
cd wiki-search-video
```
It is recommended to use a virtual environment to keep the Project's dependencies isolated <br>
Windows <br>
```bash
python3 -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
playwright install chromium
```
Mac <br>
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
playwright install chromium
```
Linux <br>
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
playwright install --with-deps chromium
```
The terminal should then indicate that the .venv is active
Running <br>
Command line <br>
```bash
python3 cli.py --term "help"
```
Tkinter GUI (App) <br>
```bash
python3 gui_tkinter.py
```
Streamlit (Web app) <br>
```bash
streamlit run gui_streamlit.py
```