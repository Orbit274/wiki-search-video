import re

def safe_filename(text: str) -> str:
        text = re.sub(r'[<>:"/\\|?*]', '_', text)
        text = text.strip(' .')
        return text or 'output'