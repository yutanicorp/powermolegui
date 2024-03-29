#!/usr/bin/env python
# -*- coding: utf-8 -*-
# File: powermolegui.py
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
Main code for powermolegui.

.. _Google Python Style Guide:
   http://google.github.io/styleguide/pyguide.html

"""

import logging.config
from powermolegui.lib.logging import LoggingHandler
from powermolegui.lib.windows import MainWindow

__author__ = '''Vincent Schouten <powermole@protonmail.com>'''
__docformat__ = '''google'''
__date__ = '''08-10-2020'''
__copyright__ = '''Copyright 2021, Vincent Schouten'''
__credits__ = ["Vincent Schouten"]
__license__ = '''MIT'''
__maintainer__ = '''Vincent Schouten'''
__email__ = '''<powermole@protonmail.com>'''
__status__ = '''Development'''  # "Prototype", "Development", "Production".


def main():
    """Main method.

    This method holds what you want to execute when
    the script is run on command line.
    """
    logger = logging.getLogger()  # Returns a logger (which enables log messages to be printed to the terminal)
    logger.setLevel(logging.DEBUG)
    main_window = MainWindow()
    logging_win_handler = LoggingHandler(main_window)  # Handlers send the log records (created by loggers) to the GUI
    logger.addHandler(logging_win_handler)
    main_window.logging_win_handler = logging_win_handler
    main_window.mainloop()
