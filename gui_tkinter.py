import logging
import threading
import queue
import os
import platform
import subprocess
import tkinter as tk
from tkinter import ttk, messagebox
from wikisearch.pipeline import generate_video

class TkinterHandler(logging.Handler):
    def __init__(self):
        super().__init__()
        self.queue = queue.Queue()

    def emit(self, record):
        self.queue.put(record)

class CollapsableFrame(ttk.Frame):
    def __init__(self, parent_frame, title):
        super().__init__(parent_frame)
        self.button = ttk.Button(self, text=f'▼ {title}', command=self.toggle)
        self.button.pack(fill='x')
        self.content = ttk.Frame(self)
        self.content.pack(fill='both', expand=True)
        self.expanded = True
        self.title = title

    def toggle(self):
        if self.expanded:
            self.content.pack_forget()
            self.button.configure(text=f'▶ {self.title}')
        else:
            self.content.pack(fill='both', expand=True)
            self.button.configure(text=f'▼ {self.title}')
        self.expanded = not self.expanded

def center_window(window, width_ratio, height_ratio):
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    width = int(screen_width * width_ratio)
    height = int(screen_height * height_ratio)
    x = (screen_width - width) // 2
    y = (screen_height - height) // 2
    window.geometry(f'{width}x{height}+{x}+{y}')

def open_video(path):
    system = platform.system()
    if system == 'Windows':
        os.startfile(path)
    elif system == 'Darwin':
        subprocess.run(['open', path])
    elif system == 'Linux':
        if 'microsoft' in platform.release().lower():
            subprocess.run(['explorer.exe', path])
        else:
            subprocess.run(['xdg-open', path])
    else:
        raise OSError(f'Unknown operating system: {system}')

def generation_finished(video_path):
    if video_path is None:
        return
    open_video_button.configure(command=lambda: open_video(video_path))
    video_frame.pack(fill='x', after=command_frame)

def generate_wrapper(term):
        try:
            video_path = generate_video(term)
            root.after(0, lambda: generation_finished(video_path))
        except Exception:
            logging.exception('Video generation failed')
        finally:
            root.after(0, lambda: generate_button.configure(state='normal'))

def generate():
    term = search_term.get().strip()
    if not term:
        messagebox.showwarning('Missing search term', 'Please enter a search term')
        return
    clear_logs()
    video_frame.pack_forget()
    progress_bar.pack(fill='x')
    if debug_enabled.get():
        debug_bar.pack(fill='x')
    generate_button.configure(state='disabled')
    worker = threading.Thread(target=generate_wrapper, args=(term,), daemon=True)
    worker.start()

def check_logs():
    while True:
        try:
            record = tkinter_handler.queue.get_nowait()
        except queue.Empty:
            break

        message = tkinter_handler.format(record)
        if record.levelno >= logging.INFO:
            if getattr(record, 'progress', False):
                progress_text.configure(state='normal')
                progress_text.delete('1.0', '2.0')
                progress_text.insert('1.0', message + '\n')
                progress_text.configure(state='disabled')
            else:
                progress_text.configure(state='normal')
                progress_text.insert('end', message + '\n')
                progress_text.configure(state='disabled')
        elif debug_enabled.get():
            debug_text.configure(state='normal')
            debug_text.insert('end', message + '\n')
            debug_text.configure(state='disabled')

    root.after(100, check_logs)

def clear_logs():
    for widget in (progress_text, debug_text):
        widget.configure(state='normal')
        widget.delete('1.0', 'end')
        widget.configure(state='disabled')

if __name__ == '__main__':
    tkinter_handler = TkinterHandler()
    logging.getLogger().addHandler(tkinter_handler)
    logging.getLogger().setLevel(logging.DEBUG)

    root = tk.Tk()
    center_window(root, 1/2, 1/2)
    root.title('WikiSearch')

    main_frame = ttk.Frame(root)
    main_frame.pack(fill='both', expand=True, padx=50, pady=30)

    title = ttk.Label(main_frame, text='WikiSearch', font=('', 20))
    title.pack()

    search_frame = ttk.Frame(main_frame)
    search_frame.pack(fill='x')
    search_term = tk.StringVar()
    search_label = ttk.Label(search_frame, text='Search term:')
    search_label.pack(anchor='w')
    term_input = ttk.Entry(search_frame, textvariable=search_term)
    term_input.pack(anchor='w')

    command_frame = ttk.Frame(main_frame)
    command_frame.pack(fill='x', pady=10)
    generate_button = ttk.Button(command_frame, text='Generate Video', command=generate)
    generate_button.pack(side='left')
    debug_enabled = tk.BooleanVar(value=False)
    debug_checkbox = ttk.Checkbutton(command_frame, text='Debug', variable=debug_enabled)
    debug_checkbox.pack(anchor='center')

    video_frame = ttk.Frame(main_frame)
    open_video_button = ttk.Button(video_frame, text='Open Video')
    open_video_button.pack(side='top')

    success_label = ttk.Label(video_frame, text='Video Generated Successfully! It can be found in the wiki-search-video directory!')
    success_label.pack(side='bottom')

    progress_bar = CollapsableFrame(main_frame, 'Generating video...')
    progress_text = tk.Text(progress_bar.content, state='disabled', height=6)
    progress_text.pack(fill='both', expand=True)
    progress_text.mark_set('screenshot_progress', '1.0')

    debug_bar = CollapsableFrame(main_frame, 'Debug')
    debug_text = tk.Text(debug_bar.content, state='disabled', height=6)
    debug_text.pack(fill='both', expand=True)

    root.after(100, check_logs)
    root.mainloop()