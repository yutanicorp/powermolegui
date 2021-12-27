#!/usr/bin/env python
# -*- coding: utf-8 -*-
# File: animation.py
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
Main code for transforming tkinter canvas items.

.. _Google Python Style Guide:
   http://google.github.io/styleguide/pyguide.html

"""

__author__ = '''Vincent Schouten <powermole@protonmail.com>'''
__docformat__ = '''google'''
__date__ = '''28-02-2021'''
__copyright__ = '''Copyright 2021, Vincent Schouten'''
__credits__ = ["Vincent Schouten"]
__license__ = '''MIT'''
__maintainer__ = '''Vincent Schouten'''
__email__ = '''<powermole@protonmail.com>'''
__status__ = '''Development'''  # "Prototype", "Development", "Production".


class AnimateItem:
    """Animates the canvas item by moving horizontally in one direction and loop."""

    def __init__(self, main_window, canvas_item):
        """Instantiates the Animate object.

        Args:
            main_window (MainWindow): An instantiated MainWindow object.
            canvas_item (CanvasItem): An instantiated CanvasItem object.

        """
        self._status = main_window.main_frame.canvas_frame.canvas_status
        self._canvas = main_window.main_frame.canvas_frame.canvas_landscape
        self._terminate = False
        self._canvas_item = canvas_item
        self._canvas_item_width = canvas_item.total_width
        self._distance = canvas_item.distance
        self._distance_index = 0
        # self._scale = 1  # IN DEVELOPMENT

    def start(self):
        """Moves a TCP/IP packet from item to another item and loop."""
        self._canvas_item.show()

        def _animate_forward():
            if not self._terminate:
                self._canvas.move(self._canvas_item.item_tag, 10, 0)
                self._distance_index += 10
                if self._distance_index >= self._distance - self._canvas_item_width:
                    start_pos = self._distance - self._canvas_item_width
                    self._canvas.move(self._canvas_item.item_tag, start_pos * -1, 0)
                    self._distance_index = 0
                self._canvas.after(25, _animate_forward)

        _animate_forward()  # note, the animation will be threaded, so after invoking this method, it continues directly

    def stop(self):
        """Stop moving the TCP/IP packet and cleanup."""
        self._terminate = True
        self._canvas.delete(self._canvas_item.item_tag)

    def pause(self):
        """Temporarily pause moving the TCP/IP package."""
        self._canvas.itemconfig(self._canvas_item.item_tag, state='hidden')

    def resume(self):
        """Resume moving the TCP/IP package."""
        self._canvas.itemconfig(self._canvas_item.item_tag, state='normal')
