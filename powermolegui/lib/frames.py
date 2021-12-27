#!/usr/bin/env python
# -*- coding: utf-8 -*-
# File: frames.py
#
# Copyright 2021 Vincent Schouten
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to
#  deal in the Software without restriction, including without limitation the
#  rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
#  sell copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
#  all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
#  FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
#  DEALINGS IN THE SOFTWARE.
#

"""
Main code for creating tkinter frames.

The frames are used as a container for other widgets.

.. _Google Python Style Guide:
   http://google.github.io/styleguide/pyguide.html

"""

import tkinter as tk
from tkinter import ttk  # allow using Tk themed widget set

__author__ = '''Vincent Schouten <powermole@protonmail.com>'''
__docformat__ = '''google'''
__date__ = '''06-12-2019'''
__copyright__ = '''Copyright 2021, Vincent Schouten'''
__credits__ = ["Vincent Schouten"]
__license__ = '''MIT'''
__maintainer__ = '''Vincent Schouten'''
__email__ = '''<powermole@protonmail.com>'''
__status__ = '''Development'''  # "Prototype", "Development", "Production".

# Constants
BACKGROUND_CANVAS = '#232729'


# Bryan Oakley: I prefer inheriting from tk.Frame just because I typically
# start by creating a frame, but it is by no means necessary.
class MainFrame(tk.Frame):  # pylint: disable=too-many-ancestors
    """Constructs an outer frame that contains a canvas and a log frame."""

    def __init__(self, parent, scale, *args, **kwargs):  # parent = MainWindow
        """Instantiates the MainFrame object."""
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent  # what's the use of parent actually?
        self.scale = scale  # IN DEVELOPMENT

        self.canvas_frame = CanvasFrame(self)
        self.log_frame = LogFrame(self)

        self.canvas_frame.pack(fill='both', expand=True)
        self.log_frame.pack(fill='both', expand=True)


# Bryan Oakley: As a general rule of thumb, if you have a class that inherits from
# a widget and it creates other widgets, those widgets should always be children of
# self or one of its descendants, never its own parent. Having a class put child
# widgets in its parent completely defeats the purpose of inheriting from tk.Frame.
class CanvasFrame(tk.Frame):  # pylint: disable=too-many-ancestors
    """Constructs a frame for the canvas widget."""

    def __init__(self, parent):  # what's the use of parent here?
        """Instantiates the CanvasFrame object."""
        tk.Frame.__init__(self, parent)
        self.parent = parent  # what's the use of parent actually?
        self.canvas_landscape = self._canvas()
        self.canvas_status = self._status()
        self._scrollbar()
        self._scroll_bind()
        # self._menu = self._pop_menu()
        self._popup_menu()

    def _canvas(self):
        canvas = tk.Canvas(master=self,
                           background=BACKGROUND_CANVAS,
                           height=140,
                           borderwidth=0,
                           highlightthickness=0)
        canvas.pack(fill="both", expand=True)
        return canvas

    def _status(self):
        status = tk.Canvas(master=self,
                           background=BACKGROUND_CANVAS,
                           height=40,
                           borderwidth=0,
                           highlightthickness=0)
        status.pack(fill="both", expand=True)
        return status

    def _scrollbar(self):
        scrollbar = ttk.Scrollbar(master=self,
                                  orient=tk.HORIZONTAL,
                                  command=self.canvas_landscape.xview)
        scrollbar.pack(fill="x", expand=False)
        self.canvas_landscape.config(xscrollcommand=scrollbar.set)

    def _scroll_bind(self):
        # enable scrolling with the mouse
        self.canvas_landscape.bind("<ButtonPress-1>", self._scroll_start)
        self.canvas_status.bind("<ButtonPress-1>", self._scroll_start)
        self.canvas_landscape.bind("<B1-Motion>", self._scroll_move)
        self.canvas_status.bind("<B1-Motion>", self._scroll_move)

    def _scroll_start(self, event):
        self.canvas_landscape.scan_mark(event.x, event.y)

    def _scroll_move(self, event):
        # parameter 'gain' tells "scan_dragto" how many pixels to move for each pixel the mouse moves
        self.canvas_landscape.scan_dragto(event.x, event.y, gain=1)

    # def do_pop(self, event):
    #     try:
    #         self._menu.tk_popup(event.x_root, event.y_root)
    #     finally:
    #         self._menu.grab_release()
    #
    # def _pop_menu(self):
    #     menu = tk.Menu(self, tearoff=0)
    #     menu.add_command(label="Info")
    #     self.canvas.bind("<Button-2>", self.do_pop)
    #     return menu

    def _popup_menu(self):  # otherwise known as "contextual menus"
        menu = tk.Menu(self, tearoff=0)
        menu.add_command(label="Info")
        if self.tk.call('tk', 'windowingsystem') == 'aqua':
            self.canvas_landscape.bind('<2>', lambda e: menu.post(e.x_root, e.y_root))  # On MacOS
            self.canvas_landscape.bind('<Control-1>', lambda e: menu.post(e.x_root, e.y_root))  # On MacOS
        else:
            self.canvas_landscape.bind('<3>', lambda e: menu.post(e.x_root, e.y_root))  # On Windows and X1


class LogFrame(tk.Frame):  # pylint: disable=too-many-ancestors
    """Constructs a frame for the text widget."""

    def __init__(self, parent):
        """Instantiates the LogFrame object."""
        tk.Frame.__init__(self, parent)
        self.text = self._widget()

    def _widget(self):
        """____________."""
        text = tk.Text(master=self,
                       width=1,  # in units of characters - not pixels
                       height=1,  # in units of characters - not pixels
                       background='white',
                       foreground='black')
        text.pack(side="left", fill="both", expand=True)
        text.configure(state='disabled')  # block the user from entering anything
        text.config(wrap='word')

        scrollbar = ttk.Scrollbar(master=self,
                                  orient=tk.VERTICAL,
                                  command=text.yview)
        scrollbar.pack(side="right", fill="y", expand=False)

        text.config(yscrollcommand=scrollbar.set)
        return text

    def insert_log_line(self, line):
        """____________."""
        self.text.configure(state='normal')
        self.text.insert('end', line + '\n')  # 1.0 refers to line 1 (start) character 0
        self.text.see("end")
        self.text.configure(state='disabled')


class CommandFrame(tk.Frame):  # pylint: disable=too-many-ancestors
    """Constructs an outer frame that contains two log frames."""

    def __init__(self, parent, *args, **kwargs):
        """Instantiates the CommandFrame object."""
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent

        self.command_entry = CommandEntry(self.parent)
        self.command_response = CommandResponse(self.parent)

        self.command_entry.pack(fill='both', expand=False)
        self.command_response.pack(fill='both', expand=True)


class CommandEntry(tk.Frame):  # pylint: disable=too-many-ancestors
    """Constructs a frame for the text widget."""

    def __init__(self, parent):
        """Instantiates the CommandEntry object."""
        tk.Frame.__init__(self, parent)
        self._label()
        self.entry = self._entry()

    def _label(self):
        label = tk.Label(self, text="Input")
        label.pack(fill='x', expand=False)

    def _entry(self):
        entry = tk.Entry(self, justify='left')
        entry.pack(fill='x', expand=False)
        entry.focus_set()
        return entry


class CommandResponse(tk.Frame):  # pylint: disable=too-many-ancestors
    """Constructs a frame for the text widget."""

    def __init__(self, parent):
        """Instantiates the CommandResponse object."""
        tk.Frame.__init__(self, parent)
        self._label()
        self.text = self._text()

    def _label(self):
        label = tk.Label(self, text="Output")
        label.pack(fill='x', expand=False)

    def _text(self):
        text = tk.Text(self,
                       width=1,  # in units of characters - not pixels
                       height=1)  # in units of characters - not pixels
        text.config(wrap='word')
        text.tag_config('warning_style', foreground="red")
        text.insert(tk.END, 'the interface does not support shell meta characters \n'
                            'such as pipe and it\'s not possible to interact with \n'
                            'programs that need a response. hit control-c to quit \n', 'warning_style')
        text.pack(fill='both', expand=True)
        return text

    # def _scrollbar(self):
    # scrollbar = ttk.Scrollbar(self.win, orient=VERTICAL, command=self.text.yview)
    # scrollbar.grid(row=3,
    #                column=1)
    # self.text.config(yscrollcommand=scrollbar.set)
