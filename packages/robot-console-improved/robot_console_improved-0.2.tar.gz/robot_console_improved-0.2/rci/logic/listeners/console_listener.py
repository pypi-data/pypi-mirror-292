import io
import sys

from rci.logic.listener import Listener

"""
Check if the DebugLibrary is installed.
If the DebugLibrary is not installed, the user will not be able to use the robot debugger.
So, because the debugger is not supported, we don't need to support a debugger and we can disable it.
"""

SUPPORT_DEBUG = True

try:
    import DebugLibrary.keywords
    from DebugLibrary.debugcmd import DebugCmd
    from DebugLibrary.steplistener import is_step_mode
except Exception as e:  # no cov
    SUPPORT_DEBUG = False


class ConsoleListener(Listener, io.StringIO):
    def __init__(self, title: str):
        super().__init__(title)
        sys.stdout = self
        sys.stderr = self

        # Overwrite the console function from robot.output.librarylogger
        sys.modules['robot'].output.librarylogger.console = self.console

        if SUPPORT_DEBUG:  # no cov
            # Overwrite the print_output function from DebugLibrary.styles
            DebugLibrary.styles.print_output = self.print_output
            # Overwrite the debug function from DebugLibrary.keywords.DebugKeywords
            DebugLibrary.keywords.DebugKeywords.debug = self.debug

        self.content: list[str] = []

    def redraw_content(self):
        """
        Updates the window content after resizing the screen
        """

        if self.scrolling_pad is None:
            return

        # Clearing the scrolling pad content
        self.scrolling_pad.clear()

        if not self.show_content:
            return

        # Getting the width and height of the scrolling pad
        height, width = self.scrolling_pad.getmaxyx()

        # Getting the content to be displayed
        content: list[str] = self.content[-height:]

        # Adding the content to the scrolling pad
        for line in content:
            self.scrolling_pad.addstr(line)

        self.scrolling_pad.noutrefresh()

    def write(self, s: str):
        """
        Overwrites the write function of the io trap
        :param s: the string to be written
        :return:
        """

        self.content.append(s)

        # If the list is bigger than max content len, delete the first x items
        if len(self.content) > self.max_content_len:
            diff = len(self.content) - self.max_content_len
            del self.content[:diff]

        # Adding the line to the scrolling pad
        if self.scrolling_pad is not None:
            height, width = self.scrolling_pad.getmaxyx()
            if height > 0:
                self.scrolling_pad.addstr(s)
                self.scrolling_pad.noutrefresh()

    def console(self, msg, newline=True, stream='stdout'):
        """
        Overwrites the console function from robot.output.librarylogger
        :param msg: the message to be printed
        :param newline: if the message should be printed in a new line
        :param stream: the stream to be used
        """

        self.write(f'\n{msg}' if newline else msg)

    def debug(self):
        """
        Overwrites the debug function from DebugLibrary.keywords.DebugKeywords
        :return:
        """

        # save stdout and redirect it to the io trap
        old_stdout = sys.stdout
        sys.stdout = self

        show_intro = not is_step_mode()
        if show_intro:
            self.print_output('\n>>>>>', 'Enter interactive shell')

        self.debug_cmd = DebugCmd()
        if show_intro:
            self.debug_cmd.cmdloop()
        else:
            self.debug_cmd.cmdloop(intro='')

        show_intro = not is_step_mode()
        if show_intro:
            self.print_output('\n>>>>>', 'Exit shell.')

        # put stdout back where it was
        sys.stdout = old_stdout

    def print_output(self, head, message, style=None):
        """
        Overwrites the print_output function from DebugLibrary.styles
        :param head: the head of the message
        :param message: the message itself
        :param style: the style of the message
        """
        self.write(f'{head} {message}\n')
