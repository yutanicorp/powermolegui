#!/usr/bin/env python
# -*- coding: utf-8 -*-
# File: items.py
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
Main code for various tkinter canvas items.

.. _Google Python Style Guide:
   http://google.github.io/styleguide/pyguide.html

"""

import uuid
import re
from time import sleep
from itertools import cycle
from abc import ABC, abstractmethod

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
FONT_SIZE = 10
THICKNESS_LINE_CLIENT = 2
THICKNESS_LINE_HOST = 2
THICKNESS_LINE_AGENT = 2
THICKNESS_LINE_TUNNEL = 1
THICKNESS_LINE_PACKET = 1
THICKNESS_PACKET = 2
WIDTH_PACKET = 20
BACKGROUND_CANVAS = '#232729'
LABEL_FONT_COLOUR = 'white'
PACKET_OUTLINE_COLOUR = '#c0c0c0'
PACKET_FILL_COLOUR = '#232729'
NON_OPERATION = 'white'
OK_COLOUR = 'green'
NOK_COLOUR = 'red'


class CanvasItem(ABC):
    """Enforces methods to be implemented for the subclassed objects."""

    def __init__(self, main_window):
        """Instantiates the CanvasItem object.

        Args:
            main_window (MainWindow): An instantiated MainWindow object.

        """
        # self.scale = main_window.scale  # IN DEVELOPMENT
        self.item_name = self._determine_item_name()
        self.item_tag = f"{self.item_name}-{self._uuid}"
        self._main_window = main_window
        self._canvas_landscape = main_window.main_frame.canvas_frame.canvas_landscape
        self._canvas_status = main_window.main_frame.canvas_frame.canvas_status
        self._item_label = 0

    @property
    def _uuid(self):
        uuid_ = f'{uuid.uuid4().hex}'
        return uuid_

    def _determine_item_name(self):
        return re.findall(r'[A-Z](?:[a-z]+|[A-Z]*(?=[A-Z]|$))', type(self).__name__)[0]  # split words at CamelCase

    def _add_label(self, item_name):
        coord_x1, coord_y1, coord_x2, _ = self._canvas_landscape.coords(self.item_tag)
        distance = coord_x2 - coord_x1
        pos_x = coord_x1 + (distance / 2)  # to determine the coordinates of the center of the shape (host/client)
        pos_y = coord_y1 - 10  # put the label a few pixels above the shape
        self._item_label = self._canvas_landscape.create_text(pos_x,
                                                              pos_y,
                                                              text=item_name,
                                                              font=('', FONT_SIZE, 'normal'),
                                                              fill=LABEL_FONT_COLOUR)

    @abstractmethod
    def create(self):
        """Creates the canvas item."""

    @abstractmethod
    def show(self):
        """Shows the canvas item."""

    @abstractmethod
    def hide(self):
        """Hides the canvas item."""

    @abstractmethod
    def setup_ok(self):
        """Colours the canvas item in accordance with an OK state."""

    @abstractmethod
    def setup_nok(self):
        """Colours the canvas item in accordance with an NOK state."""

    @abstractmethod
    def dim(self):
        """Colours the canvas item representing a non-operational state."""


class Effect:
    """Applies effects to the canvas item.

    This class provides methods to colour the canvas item in accordance with the
    operational state and provide a method to make the canvas item flicker.

    """

    def __init__(self, main_window, canvas_item, filling_type):
        """Instantiates the Effect object.

        Args:
            main_window (MainWindow): An instantiated MainWindow object.
            canvas_item (str): The ID of the canvas item on the canvas.
            filling_type (str): Either 'fill' or 'outline' depending what part of the canvas item should be coloured.

        """
        self._canvas_landscape = main_window.main_frame.canvas_frame.canvas_landscape
        self._canvas_status = main_window.main_frame.canvas_frame.canvas_status
        self._flicker_index = 0
        self._canvas_item = canvas_item
        self._filling_type = filling_type

    def flicker(self):
        """Changes the brightness of the canvas item irregularly appearing as a fluctuating light.

        The after function is threaded, so it doesn't block.

        """
        self._canvas_landscape.itemconfig(self._canvas_item, state='normal')
        colours = ['#b2b2b2', '#b2b2b2', '#7f7f7f', '#b2b2b2', 'white']
        colour_cycle = cycle(colours)
        max_elements = len(colours)

        def _flicker():
            self._flicker_index += 1
            selected_colour = next(colour_cycle)
            if self._filling_type == 'outline':
                self._canvas_landscape.itemconfig(self._canvas_item, outline=selected_colour)
                self._canvas_status.itemconfig(self._canvas_item, outline=selected_colour)
            elif self._filling_type == 'fill':
                self._canvas_landscape.itemconfig(self._canvas_item, fill=selected_colour)
                self._canvas_status.itemconfig(self._canvas_item, fill=selected_colour)
            if self._flicker_index == max_elements:
                return
            self._canvas_landscape.after(120, _flicker)
        _flicker()

    def setup_ok(self):
        """Colours the canvas item to state OK (green)."""
        arguments = {self._filling_type: OK_COLOUR}
        self._canvas_landscape.itemconfig(self._canvas_item, **arguments)
        self._canvas_status.itemconfig(self._canvas_item, **arguments)

    def setup_nok(self):
        """Colours the canvas item to state NOK (red)."""
        arguments = {self._filling_type: NOK_COLOUR}
        self._canvas_landscape.itemconfig(self._canvas_item, **arguments)
        self._canvas_status.itemconfig(self._canvas_item, **arguments)

    def dim(self):
        """Colours the canvas item to a non-operational state (white).

        To colour the outline of 'rectangles', the outline has to be configured.
        To colour the items made of 'lines', the fill has to be configured.
        """
        arguments = {self._filling_type: NON_OPERATION}
        self._canvas_landscape.itemconfig(self._canvas_item, **arguments)
        self._canvas_status.itemconfig(self._canvas_item, **arguments)


class ConnectionCalculator:
    """Calculates all properties that is needed to render a connection between two canvas items."""

    def __init__(self, main_window, canvas_item_1, canvas_item_2):
        """Instantiates the ConnectionCalculator object.

        Note: canvas.bbox doesn't return values when the item's state is 'hidden'.

        Args:
            main_window (MainWindow): An instantiated MainWindow object.
            canvas_item_1 (CanvasItem): An instantiated CanvasItem object.
            canvas_item_2 (CanvasItem): An instantiated CanvasItem object.

        """
        self._canvas_landscape = main_window.main_frame.canvas_frame.canvas_landscape
        self._component_a = self._canvas_landscape.bbox(canvas_item_1.item_tag)
        self._component_b = self._canvas_landscape.bbox(canvas_item_2.item_tag)
        self._factor = 0.05  # why is this?

    def get_connection_length_inner(self):
        """Returns the distance between two items starting from right side first item to left side second item."""
        _, _, ax2, _ = self._component_a
        bx1, _, _, _ = self._component_b
        distance = bx1 - ax2
        return distance

    def get_connection_length_outer(self):
        """Returns the distance between two items starting from right side first item to left side second item."""
        ax1, _, _, _ = self._component_a
        _, _, bx2, _ = self._component_b
        distance = bx2 - ax1
        return distance

    def get_connection_height(self):
        """Returns the height of a connection based on the height of the item."""
        _, by1, _, by2 = self._component_b
        return (by2 - by1) * self._factor  # use bbox to return the bounding box for client & host == more sophisticated

    def get_x_pos_connection_right_side(self):
        """Returns the starting position on the X-axis of the connection item."""
        _, _, ax2, _ = self._component_a
        return ax2

    def get_x_pos_connection_left_side(self):
        """Returns the starting position on the X-axis of the connection item."""
        ax1, _, _, _ = self._component_a
        return ax1

    def get_y_pos_connection(self):
        """Returns the first position on the Y-axis of the connection item."""
        _, by1, _, by2 = self._component_b
        return by1 + ((by2 - by1) / 2)


class ClientCanvasItem(CanvasItem):
    """Creates a canvas item representing a client."""

    def __init__(self, main_window, start_pos_x, start_pos_y):
        """Instantiates the ClientCanvasItem object.

        Args:
            main_window (MainWindow): An instantiated MainWindow object.
            start_pos_x (int): The position on the X-axis of the canvas item's top left corner.
            start_pos_y (int): The position on the Y-axis of the canvas item's top left corner.

        """
        super().__init__(main_window)
        self._client_effect = Effect(main_window, self.item_tag, 'outline')
        self._start_pos_x = start_pos_x
        self._start_pos_y = start_pos_y
        self._width = 90
        self._height = self._width * 0.7
        self._components = []

    def create(self):
        self._draw_outer_screen()
        self._draw_inner_screen()
        self._draw_keyboard()
        self._draw_spacebar()

    def show(self):
        self._client_effect.flicker()
        self._add_label(self.item_name)

    def hide(self):
        pass

    def _draw_outer_screen(self):
        component = self._canvas_landscape.create_rectangle(self._start_pos_x,
                                                            self._start_pos_y,
                                                            self._start_pos_x + self._width,
                                                            self._start_pos_y + self._height,
                                                            width=THICKNESS_LINE_CLIENT,
                                                            outline=NON_OPERATION,
                                                            tags=self.item_tag
                                                            # state='hidden'
                                                            )
        self._components.append(component)

    def _draw_inner_screen(self):
        coord_x1, coord_y1, coord_x2, coord_y2 = self._canvas_landscape.coords(self._components[0])
        total_width = coord_x2 - coord_x1
        total_height = coord_y2 - coord_y1
        width = (coord_x2 - coord_x1) * 0.9
        height = (coord_y2 - coord_y1) * 0.9
        start_pos_x = coord_x1 + ((total_width - width) / 2)
        start_pos_y = coord_y1 + ((total_height - height) / 2)
        component = self._canvas_landscape.create_rectangle(start_pos_x,
                                                            start_pos_y,
                                                            start_pos_x + width,
                                                            start_pos_y + height,
                                                            width=1,
                                                            outline=NON_OPERATION,
                                                            tags=self.item_tag
                                                            # state='hidden'
                                                            )
        self._components.append(component)

    def _draw_keyboard(self):
        coord_x1, coord_y1, coord_x2, coord_y2 = self._canvas_landscape.coords(self._components[0])
        width = coord_x2 - coord_x1
        total_height = coord_y2 - coord_y1
        height = (coord_y2 - coord_y1) * 0.7
        start_pos_x = coord_x1
        start_pos_y = coord_y2 + (total_height * 0.05)  # value should not be hardcoded, but calculated
        component = self._canvas_landscape.create_rectangle(start_pos_x,
                                                            start_pos_y,
                                                            start_pos_x + width,
                                                            start_pos_y + height,
                                                            width=THICKNESS_LINE_CLIENT,
                                                            outline=NON_OPERATION,
                                                            tags=self.item_tag
                                                            # state='hidden'
                                                            )
        self._components.append(component)

    def _draw_spacebar(self):
        coord_x1, coord_y1, coord_x2, coord_y2 = self._canvas_landscape.coords(self._components[2])
        total_width = coord_x2 - coord_x1
        total_height = coord_y2 - coord_y1
        width = total_width * 0.5
        height = total_height * 0.2
        start_pos_x = coord_x1 + ((total_width - width) * 0.5)
        start_pos_y = coord_y1 + ((total_height - height) * 0.8)
        component = self._canvas_landscape.create_rectangle(start_pos_x,
                                                            start_pos_y,
                                                            start_pos_x + width,
                                                            start_pos_y + height,
                                                            fill='',
                                                            width=1,
                                                            outline=NON_OPERATION,
                                                            tags=self.item_tag
                                                            # state='hidden'
                                                            )
        self._components.append(component)

    def setup_ok(self):
        self._client_effect.setup_ok()

    def setup_nok(self):
        self._client_effect.setup_nok()

    def dim(self):
        self._client_effect.dim()


class HostCanvasItem(CanvasItem):
    """Creates a canvas item representing a host."""

    def __init__(self, main_window, start_pos_x, start_pos_y, host_ip):
        """Instantiates the HostCanvasItem object.

        Args:
            main_window (MainWindow): An instantiated MainWindow object.
            start_pos_x (int): The position on the X-axis of the canvas item's top left corner.
            start_pos_y (int): The position on the Y-axis of the canvas item's top left corner.
            host_ip (str): The IP address of the Host.

        """
        super().__init__(main_window)
        self._host_effect = Effect(main_window, self.item_tag, 'outline')
        self._start_pos_x = start_pos_x
        self._start_pos_y = start_pos_y
        self._width = 90
        self._height = self._width * 1.4
        self._host_ip = host_ip

    def create(self):
        host_x1 = self._start_pos_x
        host_y1 = self._start_pos_y
        host_x2 = self._start_pos_x + self._width
        host_y2 = self._start_pos_y + self._height
        self._canvas_landscape.create_rectangle(host_x1,
                                                host_y1,
                                                host_x2,
                                                host_y2,
                                                width=THICKNESS_LINE_HOST,
                                                outline=NON_OPERATION,
                                                tags=self.item_tag,
                                                # state='hidden'
                                                )

    def show(self):
        self._host_effect.flicker()
        self._add_label(self._host_ip)

    def hide(self):
        pass

    def setup_ok(self):
        self._host_effect.setup_ok()

    def setup_nok(self):
        self._host_effect.setup_nok()

    def dim(self):
        self._host_effect.dim()


class AgentCanvasItem(CanvasItem):  # pylint: disable=too-many-instance-attributes
    """Creates a canvas item representing an Agent."""

    def __init__(self, main_window, client_canvas_item, host_canvas_items):
        """Instantiates the AgentCanvasItem object.

        Args:
            main_window (MainWindow): An instantiated MainWindow object.
            client_canvas_item (CanvasItem): An instantiated CanvasItem that represents a Client.
            host_canvas_items (list): All instantiated CanvasItems that represents a Host.

        """
        super().__init__(main_window)
        self._agent_effect = Effect(main_window, self.item_tag, 'outline')
        self._coords_client = self._canvas_landscape.coords(client_canvas_item.item_tag)
        self._coords_destination_host = self._canvas_landscape.coords(host_canvas_items[-1].item_tag)
        self._coords_agent_start_pos = None  # position of Agent next to Client
        self._coords_agent_end_pos = None  # position of Agent inside Host
        self._number_of_hosts = len(host_canvas_items)
        self._width = 0
        self._distance_index = 0
        self._distance_between_hosts = 0

    def create(self):
        self._coords_agent_end_pos = self._create_agent_derived_from_host()
        self._width = self._determine_width()
        self._coords_agent_start_pos = self._place_agent_in_client()
        self._distance_between_hosts = self._calculate_distances()

    def show(self):
        self._canvas_landscape.itemconfig(self.item_tag, dash=(9, 9), width=1, state='normal')

    def hide(self):
        pass

    def _create_agent_derived_from_host(self):
        hx1, hy1, hx2, hy2 = self._coords_destination_host
        nx1 = hx1 + 25
        ny1 = hy1 + 45
        nx2 = hx2 - 25
        ny2 = hy2 - 25
        self._canvas_landscape.create_rectangle(nx1,
                                                ny1,
                                                nx2,
                                                ny2,
                                                fill=BACKGROUND_CANVAS,
                                                width=THICKNESS_LINE_AGENT,
                                                outline=NON_OPERATION,
                                                tags=self.item_tag,
                                                # state='hidden'
                                                )
        return nx1, ny1, nx2, ny2

    def _determine_width(self):
        ax1, _, ax2, _ = self._canvas_landscape.coords(self.item_tag)
        return ax2 - ax1

    def _place_agent_in_client(self):
        _, ay1, _, ay2 = self._coords_agent_end_pos
        cx1, _, cx2, _ = self._coords_client
        center = cx1 + ((cx2 - cx1) / 2)
        nx1 = center - (self._width / 2)
        nx2 = center + (self._width / 2)
        self._canvas_landscape.coords(self.item_tag,
                                      nx1,
                                      ay1,
                                      nx2,
                                      ay2)
        return nx1, ay1, nx2, ay2

    def _calculate_distances(self):
        start_x2 = self._coords_agent_start_pos[0]  # retrieve top left position on x-axis
        end_x1 = self._coords_agent_end_pos[2]  # retrieve right bottom position on x-axis
        return (end_x1 - start_x2 - self._width) / self._number_of_hosts

    def move(self):
        """Moves the Agent item from Client item to destination Host item."""
        def _animate():
            stepper = self._distance_index / 10
            while self._distance_index > 0:
                self._canvas_landscape.move(self.item_tag, stepper, 0)
                self._distance_index -= stepper
                sleep(.02)

        self._distance_index = self._distance_between_hosts
        _animate()

    def transfer_ok(self):
        """Colours the outline white and changes the outline into a solid pattern."""
        self._canvas_landscape.itemconfig(self.item_tag,
                                          dash=(1, 1),  # default to normal, it was dash=(5, 5)
                                          outline=NON_OPERATION,
                                          width=THICKNESS_LINE_AGENT)
        self._add_label(self.item_name)

    def transfer_nok(self):
        """Colours the outline red and changes the outline to have a dashed pattern."""
        self._canvas_landscape.itemconfig(self.item_tag, dash=(5, 5), outline=NOK_COLOUR, width=THICKNESS_LINE_AGENT)

    def setup_ok(self):
        self._agent_effect.setup_ok()

    def setup_nok(self):
        self._agent_effect.setup_nok()

    def dim(self):
        self._agent_effect.dim()


class ConnectionCanvasItem(CanvasItem):  # pylint: disable=too-many-instance-attributes
    """Creates a canvas item representing a connection."""

    def __init__(self, main_window, canvas_item_1, canvas_item_2):
        """Instantiates the ConnectionCanvasItem object.

        Args:
            main_window (MainWindow): An instantiated MainWindow object.
            canvas_item_1 (CanvasItem): An instantiated CanvasItem object, representing either an Agent or a Host.
            canvas_item_2 (CanvasItem): An instantiated CanvasItem object, representing a Host.

        """
        super().__init__(main_window)
        self._connection_calculator = ConnectionCalculator(main_window, canvas_item_1, canvas_item_2)  # composition
        self._connection_effect = Effect(main_window, self.item_tag, 'fill')
        self._start_pos_x = self._connection_calculator.get_x_pos_connection_right_side()
        self._pos_y_1 = self._connection_calculator.get_y_pos_connection() - 8
        self._pos_y_2 = self._connection_calculator.get_y_pos_connection() + 8
        self._distance = self._connection_calculator.get_connection_length_inner()
        self._terminate = False
        self._distance_index = 0
        self._components = []

    def create(self):
        top_line = self._canvas_landscape.create_line(self._start_pos_x,
                                                      self._pos_y_1,
                                                      self._start_pos_x + self._distance,
                                                      self._pos_y_1,
                                                      fill=NON_OPERATION,
                                                      width=THICKNESS_LINE_TUNNEL,
                                                      tags=self.item_tag,
                                                      # state='hidden'
                                                      )
        self._components.append(top_line)
        bottom_line = self._canvas_landscape.create_line(self._start_pos_x,
                                                         self._pos_y_2,
                                                         self._start_pos_x + self._distance,
                                                         self._pos_y_2,
                                                         fill=NON_OPERATION,
                                                         width=THICKNESS_LINE_TUNNEL,
                                                         tags=self.item_tag,
                                                         # state='hidden'
                                                         )
        self._components.append(bottom_line)

    def show(self):
        self._canvas_landscape.itemconfig(self.item_tag, state='normal')

        def animate():  # blocking
            self._distance_index = self._distance
            pos_x_stepper = self._start_pos_x
            stepper = self._distance / 8
            while self._distance_index >= 0:
                self._canvas_landscape.coords(self._components[0],
                                              self._start_pos_x,
                                              self._pos_y_1,
                                              pos_x_stepper,
                                              self._pos_y_1)
                self._canvas_landscape.coords(self._components[1],
                                              self._start_pos_x,
                                              self._pos_y_2,
                                              pos_x_stepper,
                                              self._pos_y_2)
                self._distance_index -= stepper
                pos_x_stepper += stepper
                sleep(.01)
            self._add_label(self.item_name)

        animate()

    def hide(self):
        self._canvas_landscape.itemconfig(self.item_tag, state='hidden')
        self._canvas_landscape.itemconfig(self._item_label, state='hidden')

    def setup_ok(self):
        self._connection_effect.setup_ok()

    def setup_nok(self):
        self._connection_effect.setup_nok()

    def dim(self):
        pass


class StatusBannerCanvasItem(CanvasItem):
    """Creates a status banner."""

    def __init__(self, main_window):
        """Instantiates the StatusBannerCanvasItem object.

        Args:
            main_window (MainWindow): An instantiated MainWindow object.

        """
        super().__init__(main_window)
        self._tag_text_item = f"{self.item_tag}-1"
        self._tag_box_item = f"{self.item_tag}-2"
        self._text_effect = Effect(main_window, self._tag_text_item, 'fill')
        self._box_effect = Effect(main_window, self._tag_box_item, 'outline')

    def create(self):
        self._create_text()
        self._create_box()

    def _create_text(self):
        width = self._canvas_status.winfo_width()
        pos_x = width / 2
        status_height = self._canvas_status.winfo_height()
        pos_y = status_height / 2
        text = 'NO TUNNEL'.center(30)
        self._canvas_status.create_text(pos_x,
                                        pos_y,
                                        text=text,
                                        font=('', 20, 'normal'),
                                        # anchor=N,
                                        fill=NON_OPERATION,
                                        tags=self._tag_text_item)

    def _create_box(self):
        ax1, ay1, ax2, ay2 = self._canvas_status.bbox(self._tag_text_item)
        ax1 -= 20  # horizontal padding
        ax2 += 20  # horizontal padding
        ay1 -= 10  # horizontal padding
        ay2 += 10  # horizontal padding
        self._canvas_status.create_rectangle(ax1,
                                             ay1,
                                             ax2,
                                             ay2,
                                             outline=NON_OPERATION,
                                             width=THICKNESS_PACKET,
                                             tags=self._tag_box_item)

    def _show_text(self, state=None):
        if state is None:
            self._canvas_status.itemconfig(self._tag_text_item, state='normal')
            self._text_effect.flicker()
        elif state == 'opened':
            text = 'TUNNEL OPENED'.center(30)
            self._canvas_status.itemconfig(self._tag_text_item, text=text, fill=OK_COLOUR)
        elif state == 'broken':
            text = 'TUNNEL BROKEN'.center(30)
            self._canvas_status.itemconfig(self._tag_text_item, text=text, fill=NOK_COLOUR)
        elif state == 'restored':
            text = 'TUNNEL RESTORED'.center(30)
            self._canvas_status.itemconfig(self._tag_text_item, text=text, fill=OK_COLOUR)

    def _show_box(self, state=None):
        if state is None:
            self._canvas_status.itemconfig(self._tag_box_item, state='normal')
            self._box_effect.flicker()
        if state == 'opened':
            self._canvas_status.itemconfig(self._tag_box_item, outline=OK_COLOUR)
        elif state == 'broken':
            self._canvas_status.itemconfig(self._tag_box_item, outline=NOK_COLOUR)
        elif state == 'restored':
            self._canvas_status.itemconfig(self._tag_box_item, outline=OK_COLOUR)

    def show(self, state=None):  # fix pylint eror: arguments-differ / Parameters differ from overridden 'show' method
        self._show_text(state)
        self._show_box(state)

    def hide(self):
        self._canvas_status.itemconfig(self._tag_text_item, state='hidden')
        self._canvas_status.itemconfig(self._tag_box_item, state='hidden')

    def setup_ok(self):
        self._text_effect.setup_ok()
        self._box_effect.setup_ok()

    def setup_nok(self):
        pass

    def dim(self):
        text = 'TUNNEL CLOSED'.center(26)
        self._canvas_status.itemconfig(self._tag_text_item, text=text)
        self._text_effect.dim()
        self._box_effect.dim()


class PacketCanvasItem(CanvasItem):
    """Creates a visualised TCP packet."""

    def __init__(self, main_window, connection_canvas_items):
        """Instantiates the PacketCanvasItem object.

        Args:
            main_window (MainWindow): An instantiated MainWindow object.
            connection_canvas_items (list): Two instantiated CanvasItems, each representing a Connection.

        """
        super().__init__(main_window)
        self.connection_calculator = ConnectionCalculator(main_window,
                                                          connection_canvas_items[0],
                                                          connection_canvas_items[-1])
        self.total_width = WIDTH_PACKET + (2 * THICKNESS_LINE_PACKET)
        self.start_pos_x = self.connection_calculator.get_x_pos_connection_left_side()
        self.pos_y = self.connection_calculator.get_y_pos_connection()
        self.distance = self.connection_calculator.get_connection_length_outer()

    def create(self):
        self._canvas_landscape.create_rectangle(self.start_pos_x,
                                                self.pos_y - 4,
                                                self.start_pos_x + WIDTH_PACKET,
                                                self.pos_y + 4,
                                                fill=PACKET_FILL_COLOUR,
                                                outline=PACKET_OUTLINE_COLOUR,
                                                width=THICKNESS_LINE_PACKET,
                                                # state='hidden',
                                                tags=self.item_tag)

    def show(self):
        self._canvas_landscape.itemconfig(self.item_tag, state='normal')

    def hide(self):
        self._canvas_landscape.itemconfig(self.item_tag, state='hidden')

    def setup_ok(self):
        pass

    def setup_nok(self):
        pass

    def dim(self):
        pass
