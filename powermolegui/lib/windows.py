#!/usr/bin/env python
# -*- coding: utf-8 -*-
# File: windows.py
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
Main code for tkinter windows.

.. _Google Python Style Guide:
   http://google.github.io/styleguide/pyguide.html

"""

import os
import inspect
import threading
import signal
from dataclasses import dataclass
import tkinter as tk
from tkinter import DISABLED, NORMAL
from tkinter.filedialog import askopenfilename
from powermolegui.lib.logging import LoggerMixin
from powermolegui.lib.application import application
from powermolegui.lib.frames import MainFrame, CommandFrame
from powermolegui.lib.helpers import ItemsGenerator, parse_configuration_file

__author__ = '''Vincent Schouten <powermole@protonmail.com>'''
__docformat__ = '''google'''
__date__ = '''08-10-2020'''
__copyright__ = '''Copyright 2021, Vincent Schouten'''
__credits__ = ["Vincent Schouten"]
__license__ = '''MIT'''
__maintainer__ = '''Vincent Schouten'''
__email__ = '''<powermole@protonmail.com>'''
__status__ = '''Development'''  # "Prototype", "Development", "Production".

# Constants regarding powermole window for non-retina (generic) screens
WINDOW_WIDTH = 700
WINDOW_HEIGHT = 500

# Constants regarding dimensions of non-retina (generic) screen
GENERIC_SCREEN_WIDTH = 1920


def determine_scale(screen_width):
    """Sets the width of the application screen depending on type of screen."""
    if screen_width <= GENERIC_SCREEN_WIDTH:
        scale = 1
    else:  # retina screen
        scale = 2
    return scale


@dataclass
class CollectionMenuBars:
    """Holds the menu bars."""

    file_menu: tk.Menu
    execution_menu: tk.Menu
    send_menu: tk.Menu
    logging_menu: tk.Menu
    quit_menu: tk.Menu


class MainWindow(tk.Tk, LoggerMixin):
    """Represents the main window of an application.

    In an Tkinter application, the instance of the Tk class represents the main window.
    """

    def __init__(self, *args, **kwargs):
        """Instantiates the main window object."""
        tk.Tk.__init__(self, *args, **kwargs)
        LoggerMixin.__init__(self)
        signal.signal(signal.SIGINT, self._signal_handler)
        self.scale = 0
        self._script_path = self._determine_script_path()
        self._set_title_icon()
        self._set_size_window()
        self._query_windowingsystem()
        self._menu_bars = None  # holds the Tk menu bars
        self._create_menu()
        self._bind_to_event()
        self._path_config_file = None  # holds the path to the configuration file; set by _config_file_dialog()
        self.protocol("WM_DELETE_WINDOW", self.close_window)
        self.main_frame = MainFrame(self, self.scale)
        self.main_frame.pack(side="top", fill="both", expand=True)
        self.main_frame.config(highlightthickness=2)
        self._set_scrollregion(init=True)
        self.logging_win_handler = None  # holds the (instantiated) logger handler
        self.command_window = None  # holds a TopLevel widget object proving interface for user for sending commands
        self.transfer_window = None  # IN DEVELOPMENT
        self.should_terminate_application = False  # if True, the application will stop running and clean up
        self.configuration = None  # holds configuration parameters; set by show_config_graphics()
        self.canvas_items = None  # holds canvas items; generated by (Canvas)ItemGenerator
        self.instructor = None  # holds *Instructor object which provides 'send command' and 'send file' functions

    def _signal_handler(self, signum, frame):  # pylint: disable=unused-argument
        """Handles the SIGINT generated by an user when hitting Ctrl+C in the shell."""
        self.stop_application()

    def _determine_script_path(self):
        running_script = inspect.getframeinfo(inspect.currentframe()).filename  # /powermolegui/lib/windows.py
        running_script_dir = os.path.dirname(os.path.abspath(running_script))
        return os.path.dirname(running_script_dir)  # /powermolegui

    def _set_title_icon(self):
        self.title("powermole")
        path_file = os.path.join(self._script_path, 'icon', 'application_icon_tunnel.png')
        # https://stackoverflow.com/questions/11176638/tkinter-tclerror-error-reading-bitmap-file
        img = tk.PhotoImage(file=path_file)
        self.iconphoto(True, img)

    def _set_size_window(self):
        screen_width = self.winfo_screenwidth()  # width of the computer screen
        screen_height = self.winfo_screenheight()  # height of the computer screen
        self.scale = determine_scale(screen_width)  # IN DEVELOPMENT
        win_width = WINDOW_WIDTH * self.scale  # width of the main window
        win_height = WINDOW_HEIGHT * self.scale  # height of the main window
        start_x = (screen_width / 2) - (win_width / 2)
        start_y = (screen_height / 2) - (win_height / 2)
        self.geometry(f'{win_width}x{win_height}+{int(start_x)}+{int(start_y)}')
        self.resizable(True, True)
        # self._logger.info("screen size is: %s x %s", (ws, hs))  # can't work as logger is instantiated later
        print(f"screen size is: {screen_width} x {screen_height}")
        print(f"window size: {win_width} x {win_height}")

    def _query_windowingsystem(self):
        print(f"windowing system: {self.tk.call('tk', 'windowingsystem')}")

    def _create_menu(self):
        self.option_add('*tearOff', False)
        menubar = tk.Menu(self)
        file_menu = tk.Menu(menubar)
        execution_menu = tk.Menu(menubar)
        send_menu = tk.Menu(menubar)
        logging_menu = tk.Menu(menubar)
        quit_menu = tk.Menu(menubar)
        self._menu_bars = CollectionMenuBars(file_menu, execution_menu, send_menu, logging_menu, quit_menu)

        file_menu.add_command(label='Open', command=self.config_file_dialog)
        file_menu.entryconfig('Open', accelerator='Ctrl+O', state=NORMAL)
        file_menu.add_command(label='Open Recent', command=self.retrieve_recently_opened)
        file_menu.entryconfig('Open Recent', accelerator='Ctrl+T', state=NORMAL)
        menubar.add_cascade(label='File', menu=file_menu)

        execution_menu.add_command(label='Run Application', command=self.run_application)
        execution_menu.entryconfig('Run Application', accelerator='Ctrl+R', state=DISABLED)
        execution_menu.add_command(label='Stop Application', command=self.stop_application)
        execution_menu.entryconfig('Stop Application', accelerator='Ctrl+C', state=DISABLED)
        menubar.add_cascade(label='Execution', menu=execution_menu)

        send_menu.add_command(label='Send File', command=None)
        send_menu.entryconfig('Send File', accelerator='Ctrl+F', state=DISABLED)
        send_menu.add_command(label='Send Command', command=self.open_command_window)
        send_menu.entryconfig('Send Command', accelerator='Ctrl+M', state=DISABLED)
        menubar.add_cascade(label='Send', menu=send_menu)

        var_info = tk.BooleanVar()
        var_debug = tk.BooleanVar()
        logging_menu.add_checkbutton(label='Info', onvalue=1, offvalue=0, variable=var_info)
        logging_menu.add_checkbutton(label='Debug', onvalue=1, offvalue=0, variable=var_debug)
        menubar.add_cascade(label='Logging', menu=logging_menu)
        var_info.set(value=1)
        logging_menu.entryconfig('Info', state=DISABLED)
        logging_menu.entryconfig('Debug', state=DISABLED)
        # logging_win_handler.setLevel(......)  # IN DEVELOPMENT (including the code block above)

        quit_menu.add_command(label='Quit', command=self.close_window)
        quit_menu.entryconfig('Quit', accelerator='Ctrl+Q')
        menubar.add_cascade(label='Quit', menu=quit_menu)

        self.config(menu=menubar)  # self == parent = tk.Tk()

    def change_state_menu_bar_entry(self, entry, label, state):
        """Changes the state of the menu bar."""
        if entry == 'send':
            self._menu_bars.send_menu.entryconfig(label, state=state)  # the 'Send File' menu entry is in development
        elif entry == 'file':
            self._menu_bars.file_menu.entryconfig(label, state=state)
        elif entry == 'execution':
            self._menu_bars.execution_menu.entryconfig(label, state=state)

    def _bind_to_event(self):
        self.bind('<Control-o>', lambda e: self.config_file_dialog())
        self.bind('<Control-t>', lambda e: self.retrieve_recently_opened())
        self.bind('<Control-r>', lambda e: self.run_application())
        self.bind('<Control-c>', lambda e: self.stop_application())
        self.bind('<Control-f>', lambda e: None)  # IN DEVELOPMENT
        self.bind('<Control-m>', lambda e: self.open_command_window())
        self.bind('<Control-q>', lambda e: self.close_window())

    def open_command_window(self):
        """Opens interface for the user to send commands to last host and show output."""
        self.command_window = CommandWindow(self)

    def _set_scrollregion(self, init=False):
        """Sets a scroll region that encompasses all the canvas items."""
        self.main_frame.canvas_frame.canvas_landscape.update_idletasks()
        w_height = self.main_frame.canvas_frame.canvas_landscape.winfo_height()
        w_width = self.main_frame.canvas_frame.canvas_landscape.winfo_width()
        if init:
            self.main_frame.canvas_frame.canvas_landscape.config(scrollregion=(0, 0, w_width, w_height))
        else:
            # retrieve the x-axis at the far right of the last drawn item:
            _, _, x_axis_2, _ = self.main_frame.canvas_frame.canvas_landscape.bbox('all')
            if x_axis_2 <= w_width:  # if the bounding box of all items is smaller than the canvas width,
                # dismiss bounding box size
                self.main_frame.canvas_frame.canvas_landscape.config(scrollregion=(0, 0, w_width, w_height))
            else:
                self.main_frame.canvas_frame.canvas_landscape.config(scrollregion=(0, 0, x_axis_2 + 100, w_height))

    def retrieve_recently_opened(self):  # fix this py_lint error --> inconsistent-return-statements
        """Retrieves the recently opened configuration file stored in /settings."""
        path_file_recent = os.path.join(self._script_path, 'settings', 'recently_opened_config_file')
        try:
            with open(path_file_recent, encoding='utf-8') as file:
                self._path_config_file = file.read().rstrip()
        except FileNotFoundError:
            pass
        config_thread = threading.Thread(target=self._show_config_graphics)
        config_thread.start()

    def _write_to_recently_opened(self, path_config_file):
        """Stores the location to the recently opened configuration file."""
        path_file_recent = os.path.join(self._script_path, 'settings', 'recently_opened_config_file')
        with open(path_file_recent, 'w', encoding='utf-8') as file:
            file.write(path_config_file)

    def config_file_dialog(self):
        """Shows the file dialog."""
        self.main_frame.canvas_frame.canvas_landscape.delete("all")
        file_types = [('powermole config file', '*.json')]
        self._path_config_file = askopenfilename(filetypes=file_types)
        if self._path_config_file:
            config_thread = threading.Thread(target=self._show_config_graphics)
            config_thread.start()
            self._write_to_recently_opened(self._path_config_file)

    def _show_config_graphics(self):
        """Creates canvas items and shows the landscape based on the config file.

        This method is called by _config_file_dialog when
        the user opens ("Open") a powermole configuration file.
        """
        if self._path_config_file:  # return True if the variable is set with a path
            self.configuration = parse_configuration_file(self._path_config_file)  # return configuration object
            if self.configuration:
                items_generator = ItemsGenerator(self, self.configuration)
                self.canvas_items = items_generator.create_canvas_items()  # creates all canvas items
                items_generator.show_landscape(self.canvas_items)
                self._set_scrollregion()
                self.change_state_menu_bar_entry('execution', 'Run Application',
                                                 NORMAL)  # enable menu bar to start/stop application

    def run_application(self):
        """Starts the application."""
        run_thread = threading.Thread(target=application, args=(self,), name='running_application')
        run_thread.start()
        self.change_state_menu_bar_entry('file', 'Open', DISABLED)
        self.change_state_menu_bar_entry('file', 'Open Recent', DISABLED)
        self.change_state_menu_bar_entry('execution', 'Run Application', DISABLED)
        self.change_state_menu_bar_entry('execution', 'Stop Application', NORMAL)

    def stop_application(self):
        """Sets the should_terminate var to True.

        The application is running indefinitely until the user
        hits ctrl + c in the window. The window widget will
        capture the event, and sets the var should_terminate to True.
        The application, polling this var, will break the loop,
        and dismantles the tunnel.
        """
        self.should_terminate_application = True

    def close_window(self):
        """Closes the window."""

        def _is_thread_application_running():
            result = False
            for thread in threading.enumerate():
                if thread.name == 'running_application':
                    result = True
            return result

        if _is_thread_application_running():
            self._logger.info('*** window _cannot_ be closed as Tunnel is operational (press Ctrl+c) ***')
        else:
            self.destroy()


class CommandWindow(tk.Toplevel):
    """Represents an interface for the user to send commands to destination host and show output."""

    def __init__(self, parent, *args, **kwargs):
        """Instantiates the TopLevel object."""
        super().__init__(*args, **kwargs)
        self._bind_to_event()
        self._is_return_pressed = False
        self._set_size()
        self.instructor = parent.instructor
        self.scale = 0
        self.title("Interface")
        self.protocol("WM_DELETE_WINDOW", self.close_window)
        self.sub_command_window = CommandFrame(self)

    def _bind_to_event(self):
        self.bind("<Return>", lambda e: self.send_command())
        self.bind('<Control-c>', lambda e: self.close_window())

    def _set_size(self):
        screen_width = self.winfo_screenwidth()  # width of the computer screen
        screen_height = self.winfo_screenheight()  # height of the computer screen
        self.scale = determine_scale(screen_width)
        win_width = WINDOW_WIDTH * 0.7  # width of the main window
        win_height = WINDOW_HEIGHT * 0.7  # height of the main window
        start_x = (screen_width / 2) - (win_width / 2)
        start_y = (screen_height / 2) - (win_height / 2)
        # self.geometry('%dx%d+%d+%d' % (win_width, win_height, start_x, start_y))  # geometry behaves erratic!
        self.geometry(f'{win_width}x{win_height}+{start_x}+{start_y}')  # geometry behaves erratic!
        self.resizable(True, True)

    def close_window(self):
        """Closes this top level widget."""
        self.destroy()

    def send_command(self):
        """Captures the input of the user and shows output returned from *Instructor."""
        input_ = self.sub_command_window.command_entry.entry.get()
        self.sub_command_window.command_entry.entry.delete(0, 'end')
        self._is_return_pressed = False
        output = self.instructor.send_command(input_)
        self._parse_output(output)

    def _parse_output(self, output):
        output_str = output.decode("utf-8")
        output_line = output_str.split('\n')
        for line in output_line:
            self.sub_command_window.command_response.text.insert('end', line + '\n')
            self.sub_command_window.command_response.text.see("end")
        self.sub_command_window.command_response.text.insert('end', '\n')


class TransferWindow(tk.Toplevel):
    """Represents an interface for the user to select files locally to be copied to destination host.

    IN DEVELOPMENT!
    """

    def __init__(self, *args, **kwargs):
        """Instantiates the TopLevel object."""
        super().__init__(*args, **kwargs)  # with super(), no self as argument is needed
        self.scale = 0
        self.title("Interface")
        self._set_size()

    def _set_size(self):
        screen_width = self.winfo_screenwidth()  # width of the computer screen
        screen_height = self.winfo_screenheight()  # height of the computer screen
        self.scale = determine_scale(screen_width)
        win_width = WINDOW_WIDTH * 0.7  # width of the main window
        win_height = WINDOW_HEIGHT * 0.7  # height of the main window
        start_x = (screen_width / 2) - (win_width / 2)
        start_y = (screen_height / 2) - (win_height / 2)
        # self.geometry('%dx%d+%d+%d' % (win_width, win_height, start_x, start_y))  # geometry behaves erratic!
        self.geometry(f'{win_width}x{win_height}+{start_x}+{start_y}')  # geometry behaves erratic!
        self.resizable(True, True)
