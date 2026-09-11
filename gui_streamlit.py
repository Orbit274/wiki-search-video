import logging
import streamlit as st
from wikisearch.pipeline import generate_video

STYLES_CSS = '''
    <style>
        .block-container {
            max-width: 760px;
            padding-top: 15px;
        }

        .subtitle {
            font-size: 16px;
            color: #7d8499;
            margin: -15px 0px 10px 0px
        }

        .stButton > button {
            background-color: #ff4b4b;
            color: white;
            border: none;
            border-radius: 8px;
            font-weight: 600;
            padding: 10px 20px;
        }

        .stButton > button:hover {
            background-color: #ff3838;
            color: white;
        }

        .video-placeholder {
            height: 427.5px;
            background-color: #1f2023;
            border-radius: 9px;
            display: flex;
            align-items: center;
            justify-content: center;
            color: #9a9da5;
            font-size: 16px;
        }
    </style>
'''

class StreamlitHandler(logging.Handler):
    def __init__(self, status, progress_placeholder, debug_container, debug_enabled):
        super().__init__()
        self.status = status
        self.progress_placeholder = progress_placeholder
        self.debug_container = debug_container
        self.debug_enabled = debug_enabled

    def emit(self, record):
        message = self.format(record)
        if record.levelno >= logging.INFO:
            if getattr(record, 'progress', None):
                self.progress_placeholder.write(message)
            else:
                self.status.write(message)
        elif self.debug_enabled:
            self.debug_container.write(message)

if __name__ == '__main__':
    st.set_page_config(page_title='WikiSearch')
    st.markdown(STYLES_CSS, unsafe_allow_html=True)
    st.title('WikiSearch')
    st.markdown(
        '''
        <div class="subtitle">
        Generate a video collage of Wikipedia occurrences of a word
        </div>
        ''',
        unsafe_allow_html=True
    )

    search_term = st.text_input('Search term', placeholder='Python')
    col1, col2 = st.columns([2, 1])
    generate = col1.button('Generate Video')
    debug = col2.checkbox('Debug mode')
    video_placeholder = st.empty()
    success_placeholder = st.empty()
    location_placeholder = st.empty()
    status_placeholder = st.empty()
    debug_placeholder = st.empty()

    video_placeholder.markdown(
        '''
        <div class="video-placeholder">
            Video will appear here
        </div>
        ''',
        unsafe_allow_html=True
    )

    if generate:
        if not search_term:
            st.warning('Please enter a search term')
        else:
            if debug:
                debug_container = debug_placeholder.status('Debug', expanded=True)
            else:
                debug_container = None
                
            with status_placeholder.container():
                status = st.status('Generating video...', expanded=True)
                progress_placeholder = status.empty()

                handler = StreamlitHandler(status, progress_placeholder, debug_container, debug)
                logger = logging.getLogger('wikisearch')
                logger.setLevel(logging.DEBUG)
                logger.addHandler(handler)

                try:
                    video = generate_video(search_term)
                finally:
                    logger.removeHandler(handler)
                if video is None:
                    status.write('No video generated')
                status.update(state='complete')
                if debug:
                    debug_container.update(state='complete')

            if video is not None:
                video_placeholder.video(video)
                success_placeholder.success(f'Video generated: {search_term}.mp4')
                location_placeholder.write(f'File available in the wiki-search-video directory')