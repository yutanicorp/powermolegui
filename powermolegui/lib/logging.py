#!/usr/bin/env python
# -*- coding: utf-8 -*-
# File: logging.py
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
Main code for logging.

.. _Google Python Style Guide:
   http://google.github.io/styleguide/pyguide.html

"""

import logging

__author__ = '''Vincent Schouten <powermole@protonmail.com>'''
__docformat__ = '''google'''
__date__ = '''08-10-2020'''
__copyright__ = '''Copyright 2021, Vincent Schouten'''
__credits__ = ["Vincent Schouten"]
__license__ = '''MIT'''
__maintainer__ = '''Vincent Schouten'''
__email__ = '''<powermole@protonmail.com>'''
__status__ = '''Development'''  # "Prototype", "Development", "Production".


LOGGER_BASENAME = '''powermolegui'''


class LoggerMixin:
    """Contains a logger method for use by other classes."""

    def __init__(self):
        """Initialize the LoggerMixin object."""
        self._logger = logging.getLogger(f'{LOGGER_BASENAME}.{self.__class__.__name__}')


class LoggingHandler(logging.Handler):
    """A handler for sending logging events to LoggingWindow.

    Handlers send the log records (created by loggers) to the appropriate destination.
    In this case, it invokes the insert_log_line() of LoggingWindow and passes the
    filtered message (for log level INFO) to be rendered on screen in the GUI.
    """

    def __init__(self, main_window):
        """___________."""
        super().__init__(level=logging.INFO)
        self.logger = main_window.main_frame.log_frame

    def emit(self, record):
        msg = self.format(record)
        self.logger.insert_log_line(msg)
