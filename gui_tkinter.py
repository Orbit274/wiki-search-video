import logging
import threading
import os
import platform
import subprocess
import tkinter as tk
from tkinter import ttk, messagebox
from wikisearch.pipeline import generate_video

class TkinterHandler(logging.Handler):
    pass

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

if __name__ == '__main__':
    root = tk.Tk()
    center_window(root, 1/2, 1/2)
    root.title('WikiSearch')

    main_frame = ttk.Frame(root)
    main_frame.pack(fill='both', expand=True, padx=50, pady=30)

    search_frame = ttk.Frame(main_frame)
    search_frame.pack(fill='x')
    search_term = tk.StringVar()
    search_label = ttk.Label(search_frame, text='Search term:')
    search_label.pack(anchor='w')
    term_input = ttk.Entry(search_frame, textvariable=search_term)
    term_input.pack(anchor='w')

    command_frame = ttk.Frame(main_frame)
    command_frame.pack(fill='x', pady=10)
    generate_button = ttk.Button(command_frame, text='Generate Video', command=generate_video)
    generate_button.pack(side='left')
    debug_enabled = tk.BooleanVar(value=False)
    debug_checkbox = ttk.Checkbutton(command_frame, text='Debug', variable=debug_enabled)
    debug_checkbox.pack(side='top')

    video_frame = ttk.Frame(main_frame)
    video_placeholder = ttk.Label(video_frame, text='Video will appear here')

    progress_bar = CollapsableFrame(main_frame, 'Generating video...')
    progress_bar.pack(fill='x')
    progress_text = tk.Text(progress_bar.content, state='disabled', height=6)
    progress_text.pack(fill='both', expand=True)

    debug_bar = CollapsableFrame(main_frame, 'Debug')
    debug_bar.pack(fill='x')
    debug_text = tk.Text(debug_bar.content, state='disabled', height=6)
    debug_text.pack(fill='both', expand=True)

    root.mainloop()