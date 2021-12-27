#!/usr/bin/env python
# -*- coding: utf-8 -*-
# File: helpers.py
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
Import all parts from helpers here.

.. _Google Python Style Guide:
   http://google.github.io/styleguide/pyguide.html
"""
import logging
import threading
from time import sleep
from powermolelib import Configuration
from powermolelib.powermolelibexceptions import InvalidConfigurationFile
from powermolegui.lib.logging import LoggerMixin, LOGGER_BASENAME as ROOT_LOGGER_BASENAME
from powermolegui.lib.items import ClientCanvasItem, HostCanvasItem, ConnectionCanvasItem, AgentCanvasItem, \
    PacketCanvasItem, StatusBannerCanvasItem
from powermolegui.powermoleguiexceptions import SetupFailed

__author__ = '''Vincent Schouten <powermole@protonmail.com>'''
__docformat__ = '''google'''
__date__ = '''08-10-2020'''
__copyright__ = '''Copyright 2021, Vincent Schouten'''
__credits__ = ["Vincent Schouten"]
__license__ = '''MIT'''
__maintainer__ = '''Vincent Schouten'''
__email__ = '''<powermole@protonmail.com>'''
__status__ = '''Development'''  # "Prototype", "Development", "Production".

# This is the main prefix used for logging.
logging.basicConfig(format='%(asctime)s %(name)s %(levelname)s %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')
LOGGER = logging.getLogger(f'{ROOT_LOGGER_BASENAME}.helpers')  # non-class objects like fn will consult this object


def parse_configuration_file(config_file_path):
    """Parses the configuration file to a (dictionary) object."""
    try:
        configuration = Configuration(config_file_path)
    except InvalidConfigurationFile:
        return None
    if configuration.mode == 'FOR':
        LOGGER.info('mode FOR enabled')
    elif configuration.mode == 'TOR':
        LOGGER.info('mode TOR enabled')
    elif configuration.mode == 'PLAIN':
        LOGGER.info('mode PLAIN enabled')
    return configuration


class ItemsGenerator(LoggerMixin):
    """Creates items for the components Client, Connection(s), Host(s) and Agent."""

    def __init__(self, main_window, configuration):
        """Instantiates the ShapeGenerator object."""
        super().__init__()
        # self.scale = main_window.scale  # IN DEVELOPMENT
        self._main_window = main_window
        self._config = configuration
        self._status = main_window.main_frame.canvas_frame.canvas_status
        self._canvas = main_window.main_frame.canvas_frame.canvas_landscape
        self._iteration = 0
        self._quit = False
        self._wipe_canvas()

    def _wipe_canvas(self):
        self._canvas.delete("all")

    def create_canvas_items(self):
        """Create all items and hide.

        The number of host items are derived on the total amount of hosts.
        The ConnectionCanvasItem needs not-hidden items to create a connection_canvas_item as it uses bbox.
        Bbox cannot work with hidden items.
        Once all canvas items are created, they are hidden.

        Returns:
            A list containing items. Each type of item has its own position:
            • element 0: client - the Client is given an unique position on the X-axis.
            • element 1: [hosts] - each Host is given an unique position on the X-axis.
            • element 2: [connection] - each Connection is given its from and to destination.
            • element 3: agent - an Agent is a 'child' of the target destination host.

        """
        start_y_pos = 60
        start_x_pos = 70
        amount_hosts = len(self._config.gateways) + 1
        client_item = ClientCanvasItem(self._main_window, start_x_pos, start_y_pos)
        client_item.create()
        host_items = []
        connection_items = []
        for i in range(amount_hosts):
            start_x_pos += 220
            host_item = HostCanvasItem(self._main_window, start_x_pos, start_y_pos, self._config.all_host_addr[i])
            host_item.create()
            host_items.append(host_item)
            if i == 0:
                connection_item = ConnectionCanvasItem(self._main_window, client_item, host_items[i])
            else:
                connection_item = ConnectionCanvasItem(self._main_window, host_items[i - 1], host_items[i])
            connection_item.create()
            connection_items.append(connection_item)
        agent_item = AgentCanvasItem(self._main_window, client_item, host_items)
        agent_item.create()
        packet_item = PacketCanvasItem(self._main_window, connection_items)
        packet_item.create()
        status_item = StatusBannerCanvasItem(self._main_window)
        status_item.create()
        self._status.itemconfig('all', state='hidden')
        self._canvas.itemconfig('all', state='hidden')
        return client_item, host_items, connection_items, agent_item, packet_item, status_item

    def show_landscape(self, canvas_items):  # pylint: disable=no-self-use
        """Shows the shapes of Client and Host(s).

        Modifying the scroll region only works after the items
        have been changed ("configured") from hidden to normal.

        """
        client_item, host_items, _, _, _, status_item = canvas_items
        sleep(0.5)  # otherwise the drawing begins earlier than the eye notices
        client_item.show()  # show client item
        for host in host_items:  # show host items
            host.show()
            sleep(0.1)  # to allow this host to finish flickering before the next host is shown
        status_item.show()


class ClientAdapter:
    """Adapts a client object to a representational state for the GUI."""

    def __init__(self, item):
        """Instantiates the ClientAdapter object."""
        self.item = item

    def __str__(self):
        return 'Client'

    def stop(self):
        """Stops."""
        self.item.dim()
        return True


class TunnelAdapter:
    """Adapts a tunnel object to a representational state for the GUI."""

    def __init__(self, object_, items):
        """Instantiates the TunnelAdapter object."""
        self.object_ = object_
        self.items = items

    def __str__(self):
        return 'Tunnel'

    def stop(self):
        """Stops."""
        for item in self.items:
            item.hide()
        return self.object_.stop()


class HostAdapter:
    """Adapts a host object to a representational state for the GUI."""

    def __init__(self, items):
        """Instantiates the HostAdapter object."""
        self.items = items

    def __str__(self):
        return 'Host'

    def stop(self):
        """Stops."""
        for host in self.items:
            host.dim()
        return True


class AgentAdapter:
    """Adapts an agent object to a representational state for the GUI."""

    def __init__(self, item):
        """Instantiates the AgentAdapter object."""
        self.item = item

    def __str__(self):
        return 'Agent'

    def stop(self):
        """Stops."""
        self.item.dim()
        return True


class SetupLink(LoggerMixin):  # pylint: disable=too-many-instance-attributes
    """Establishes a connection to target destination host via intermediaries by starting various objects.

    This function also passes the instantiated objects to the StateManager, which
    will stop the Tunnel and Instructor after a KeyboardInterrupt.
    """

    def __init__(self, state, transfer_agent, tunnel, bootstrap_agent, instructor,  # pylint: disable=too-many-arguments
                 client_item, host_items, agent_item, connection_items):
        """Instantiates the SetupLink object.

        Args:
            state (StateManager): An instantiated StateManager object.
            transfer_agent (TransferAgent): An instantiated TransferAgent object.
            tunnel (Tunnel): An instantiated Tunnel object.
            bootstrap_agent (BootstrapAgent): ...
            instructor (Instructor): ...
            client_item (ClientCanvasItem): ...
            host_items (HostCanvasItem): ...
            agent_item (AgentCanvasItem): ...
            connection_items (ConnectionCanvasItem): ...

        """
        super().__init__()
        self._is_terminate_query_scp = False
        self._is_terminate_query_ssh = False
        self._state = state
        self._transfer_agent = transfer_agent
        self._tunnel = tunnel
        self._bootstrap_agent = bootstrap_agent
        self._instructor = instructor
        self._client_item = client_item
        self._host_items = host_items
        self._agent_item = agent_item
        self._connection_items = connection_items

    def start(self):
        """Starts setting up link."""
        self.start_client()
        self.start_transfer_agent()
        self.start_tunnel()
        self.start_bootstrap_agent()
        self.start_instructor()

    def _query_transfer_agent_connection(self):
        """Moves the Agent canvas item every time the tunnel.authenticated_hosts is appended with a new host."""
        self._logger.debug('querying for authenticated hosts...')
        index = 0
        while index < len(self._transfer_agent.all_host_addr):
            # show 1st move
            if index == 0 and self._transfer_agent.all_host_addr[index] in self._transfer_agent.authenticated_hosts:
                self._agent_item.move()  # blocking
                index += 1
            # show nth move
            elif index > 0 and self._transfer_agent.all_host_addr[index] in self._transfer_agent.authenticated_hosts:
                self._agent_item.move()  # blocking
                index += 1
            if self._is_terminate_query_scp:
                break
            sleep(0.1)  # otherwise, tk might behaves erratic

    def _query_ssh_proxyjump_connection(self):
        """Shows a new Connection canvas item every time the tunnel.authenticated_hosts is appended with a new host."""
        self._logger.debug('querying for authenticated hosts...')
        index = 0
        while index < len(self._tunnel.all_host_addr):
            if index == 0 and self._tunnel.all_host_addr[index] in self._tunnel.authenticated_hosts:  # show 1st conn.
                self._connection_items[index].show()  # blocking
                index += 1
            elif index > 0 and self._tunnel.all_host_addr[index] in self._tunnel.authenticated_hosts:  # show nth conn.
                self._connection_items[index].show()  # blocking
                index += 1
            if self._is_terminate_query_ssh:
                break
            sleep(0.1)  # otherwise, tk might behaves erratic

    def start_client(self):
        """Shows the client item.

        This method also adds the instance of the client adapter to the context manager.

        """
        self._state.add_object(ClientAdapter(self._client_item))
        self._client_item.setup_ok()

    def start_transfer_agent(self):
        """Starts transferring Agent to destination host."""
        # the TransferAgent object is a disposable one-trick pony
        # no need to invoke state.add_object()
        self._agent_item.show()
        thread = threading.Thread(target=self._query_transfer_agent_connection)
        thread.start()
        if not self._transfer_agent.start():
            self._agent_item.transfer_nok()
            self._is_terminate_query_scp = True
            raise SetupFailed(self._transfer_agent)
        while thread.is_alive():
            sleep(0.5)
        self._logger.info('Agent has been transferred securely to destination host')
        self._agent_item.transfer_ok()
        sleep(0.25)  # give the user some time to follow all activity on the canvas

    def start_tunnel(self):
        """Starts setting up the Tunnel with forwarded connections used by Instructor."""
        self._state.add_object(TunnelAdapter(self._tunnel, self._connection_items))
        self._state.add_object(HostAdapter(self._host_items))
        thread = threading.Thread(target=self._query_ssh_proxyjump_connection)
        thread.start()
        if not self._tunnel.start():
            for conn, host in zip(self._connection_items, self._host_items):
                conn.setup_nok()
                host.setup_nok()
            self._is_terminate_query_ssh = True
            raise SetupFailed(self._tunnel)
        self._logger.info('Tunnel has been opened...')
        while thread.is_alive():
            sleep(0.5)
        for conn, host in zip(self._connection_items, self._host_items):
            sleep(0.1)
            conn.setup_ok()
            host.setup_ok()
        sleep(0.25)  # give the user some time to follow all activity on the canvas

    def start_bootstrap_agent(self):
        """Starts bootstrapping the agent by executing agent module on destination host."""
        # the BootstrapAgent object is a disposable one-trick pony
        if not self._bootstrap_agent.start():
            self._agent_item.setup_nok()
            raise SetupFailed(self._bootstrap_agent)
        self._logger.info('Agent has been executed')
        self._agent_item.setup_ok()

    def start_instructor(self):
        """Starts the Instructor and checks if the Agent can be reached."""
        self._state.add_object(self._instructor)
        self._state.add_object(AgentAdapter(self._agent_item))
        if not self._instructor.start():
            raise SetupFailed(self._instructor)
        self._logger.info('Instructor has been executed')


class StateVisualiser:  # pylint: disable=too-few-public-methods
    """Shows the state of the encrypted tunnel by a banner and by visualising the packet flow."""

    def __init__(self, heartbeat, animated_packet, status_item):
        """Instantiates the StateVisualiser object.

        Args:
            animated_packet: ...
            heartbeat: An instantiated Heartbeat context manager object which determines periodically the
                        state of the tunnel.
            status_item: ...

        """
        self._animated_packet = animated_packet
        self._heartbeat = heartbeat
        self._status_item = status_item

    def start(self):
        """Start continuously determining the state of the tunnel."""
        self._status_item.show('opened')
        self._animated_packet.start()
        while not self._heartbeat.terminate:
            if not self._heartbeat.is_tunnel_intact:
                self._status_item.show('broken')
                self._animated_packet.pause()
                while not self._heartbeat.is_tunnel_intact:
                    sleep(0.2)
                self._status_item.show('restored')
                self._animated_packet.resume()
            sleep(0.2)
        self._animated_packet.stop()
        self._status_item.dim()
