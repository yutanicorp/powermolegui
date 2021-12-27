#!/usr/bin/env python
# -*- coding: utf-8 -*-
# File: daemon.py
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
Main code for daemon.

.. _Google Python Style Guide:
   http://google.github.io/styleguide/pyguide.html

"""

import os
import sys
import atexit
import signal
from abc import ABC
from time import sleep

__author__ = '''Vincent Schouten <powermole@protonmail.com>'''
__docformat__ = '''google'''
__date__ = '''25-12-2021'''
__copyright__ = '''Copyright 2021, Vincent Schouten'''
__credits__ = ["Vincent Schouten"]
__license__ = '''MIT'''
__maintainer__ = '''Vincent Schouten'''
__email__ = '''<powermole@protonmail.com>'''
__status__ = '''Development'''  # "Prototype", "Development", "Production".


class Daemon(ABC):
    """Instantiates the daemon."""

    def __init__(self, pid_file=None, stdout=None, stderr=None):
        self.stdout = stdout or './daemon_out.log'
        self.stderr = stderr or './daemon_err.log'
        self.pid_file = pid_file or './daemon.pid'

    def _remove_pid(self):
        """Deletes the pid file."""
        os.remove(self.pid_file)

    def _daemonize(self):
        """Double forking of the process."""
        # fork 1 to spin off the child that will spawn the daemon.
        if os.fork() > 0:
            sys.exit(0)  # exit first parent
        # This is the child.
        # 1. clear the session id to clear the controlling TTY.
        # 2. set the umask so we have access to all files created by the daemon.
        os.setsid()
        os.umask(0)

        # fork 2 ensures we can't get a controlling TTY [ttd]?
        if os.fork() > 0:
            sys.exit(0)  # exit from second parent
        # This is a child that can't ever have a controlling TTY.

        # ------- VSCHOUTE 2021-12-25: the execution flow stops here

        # redirect standard file descriptor for *stdin* (essentially shut down stdin)
        with open('/dev/null', 'r') as dev_null:
            os.dup2(dev_null.fileno(), sys.stdin.fileno())  # os.dup <-- duplicate file descriptor

        # redirect standard file descriptor for *stderr* to log file
        sys.stderr.flush()
        with open(self.stderr, 'a+') as stderr:
            os.dup2(stderr.fileno(), sys.stderr.fileno())  # os.dup <-- duplicate file descriptor

        # redirect standard file descriptor for *stdout* to log file
        sys.stdout.flush()
        with open(self.stdout, 'a+') as stdout:
            os.dup2(stdout.fileno(), sys.stdout.fileno())  # os.dup <-- duplicate file descriptor

        # registered functions are executed automatically when the interpreter session is terminated normally.
        atexit.register(self._remove_pid)

        #   py interpreter
        #    |
        #   (fork) < duplicate itself
        #    |
        #    ├─ parent < exit this process!
        #    |
        #   (setsid) < detach from the terminal (ie. no controlling TTY) to avoid certain signals
        #    |
        #   (fork) < duplicate itself
        #    |
        #    ├─ parent < exit this process!
        #    |
        #    └─ child < store the pid of this process
        #
        pid = str(os.getpid())

        # write pid to file
        with open(self.pid_file, 'w') as pid_f:
            pid_f.write('{0}'.format(pid))

    @property
    def pid(self):
        """Returns the pid read from the pid file."""
        try:
            with open(self.pid_file, 'r') as pid_file:
                pid = int(pid_file.read().strip())
            return pid
        except IOError:
            return

    def start(self, function):
        """Starts the daemon."""
        # print('Starting...')
        if self.pid:
            print(('PID file {0} exists. '
                   'Is the daemon already running?').format(self.pid_file))
            sys.exit(1)
        self._daemonize()
        function()

    def stop(self):
        """Stops the daemon."""
        if not self.pid:
            print(("PID file {0} doesn't exist. "
                   "Is the daemon not running?").format(self.pid_file))
            return
        try:
            while 1:
                os.kill(self.pid, signal.SIGTERM)
                sleep(1)
        except OSError as err:
            if 'No such process' in err.strerror and \
                    os.path.exists(self.pid_file):
                os.remove(self.pid_file)
            else:
                print(err)
                sys.exit(1)

    def restart(self, function):
        """Restarts the daemon."""
        self.stop()
        self.start(function)
