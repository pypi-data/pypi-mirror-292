import curses
import os
import shutil
import threading
import time
from typing import TYPE_CHECKING

from rci.logic.listeners.input_listener import SUPPORT_DEBUG, InputListener

if TYPE_CHECKING:
    from rci.logic.listener import Listener


class Interface:
    def __init__(self):
        self.screen: curses.window | None = None
        self._is_running = True
        self.debug_console: InputListener | None = None
        self.thread: threading.Thread | None = None
        self.listeners: list['Listener'] = []

        self.create_interface()

    @property
    def is_running(self):
        return self._is_running

    @is_running.setter
    def is_running(self, value):
        self._is_running = value

    def create_interface(self):
        """
        Creates the interface
        """

        # Creates the main screen
        self.screen = curses.initscr()
        # Hides the cursor
        curses.curs_set(0)
        # Disables the automatic echoing of keys to the screen
        curses.noecho()
        # Enables the reading of keys instantly, without waiting for enter to be pressed
        curses.cbreak()
        # Enables the reading of special keys like the arrow keys
        self.screen.keypad(True)

        # Creating the debug console, but not showing it
        if SUPPORT_DEBUG:  # no cov
            self.debug_console = InputListener(self.screen)
            self.debug_console.active = True

    def add_listener(self, listener: 'Listener'):
        """
        Adds the listener to the interface and sets the main window of it
        :param listener: the listener
        """

        listener.main_window = self.screen
        self.listeners.append(listener)

    def create_windows(self, refresh: bool = True):
        """
        Creates the sub windows
        """

        # Get the size of the terminal
        term_lines, term_columns = self.screen.getmaxyx()

        # Calculates the number of active windows
        active_windows = sum(window.active for window in self.listeners)

        if active_windows == 0:
            return

        debug_console_height = 4

        if self.debug_console:
            if self.debug_console.active:
                term_lines -= debug_console_height

        # Check how many lines are available for the windows
        window_height = term_lines // active_windows

        offset = 0

        # Resize the windows
        for listener in self.listeners:
            # If the listener is not active, skip it
            if not listener.active:
                continue

            # If the display could not be created, the window is too small and show message
            if not listener.create_display(window_height, term_columns, offset):
                return False

            offset += window_height

        # Create the debug console
        if self.debug_console:
            if self.debug_console.active:
                self.debug_console.create_display(debug_console_height, term_columns, offset)

        # Check if the screen needed to be refreshed
        if refresh:
            self.screen.refresh()

        return True

    def resize_windows(self, term_size: os.terminal_size) -> bool:
        """
        Resizes the sub windows
        :return: True if the windows are resized, otherwise False
        """

        # Removing existing content on the window and resize the main screen
        self.screen.erase()
        self.screen.refresh()
        self.screen.resize(term_size.lines, term_size.columns)

        if not self.create_windows(refresh=False):
            self.resize_message()
            for listener in self.listeners:
                # Disable the content of the listeners
                listener.show_content = False
            return

        for listener in self.listeners:
            listener.show_content = True
            # Redraw the content of the listeners
            if listener.active:
                # Enable the content of the listeners
                listener.redraw_content()

        # Redraw the windows
        self.screen.redrawwin()
        self.screen.refresh()

        return

    def update_windows(self):
        """
        Updates the sub windows
        :return:
        """

        for listener in self.listeners:
            if listener.active:
                listener.update_content()

    def start_interface(self):
        """
        Shows the interface
        """
        self.thread = threading.Thread(target=self.update_interface)
        self.thread.start()

    def update_interface(self):
        """
        Updates the interface
        """

        size = shutil.get_terminal_size()

        while self.is_running:
            if size != shutil.get_terminal_size():
                size = shutil.get_terminal_size()
                self.resize_windows(size)

            else:
                for listener in self.listeners:
                    if listener.need_full_redraw:
                        listener.redraw_content()

            curses.doupdate()

            time.sleep(1)

    def resize_message(self):
        """
        Displays a message on the screen, indicating that the terminal is too small
        """
        self.screen.erase()
        self.screen.addstr("Terminal window is too small.")
        self.screen.refresh()

    def stop_curses(self):
        """
        Properly shuts down the curses window
        """
        curses.nocbreak()
        self.screen.keypad(False)
        curses.echo()
        curses.curs_set(1)
        curses.endwin()

    def exit(self):
        """
        Exits the interface
        """

        curses.doupdate()
        self.is_running = False

        while True:
            key = self.screen.getch()
            if key == ord("q"):
                self.stop_curses()
                break
