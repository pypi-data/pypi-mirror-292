import logging

from rci.logic.listener import Listener


class Handler(logging.Handler):
    def __init__(self, format, listener):
        super().__init__()
        self.log_format = format
        self.listener = listener

    def emit(self, record: logging.LogRecord):
        """
        Writes the log to the window
        :param record: the log record
        """
        line = '\n' + self.log_format(record)
        self.listener.content.append(line)

        # If the list is bigger than max content len, delete the first x items
        if len(self.listener.content) > self.listener.max_content_len:
            diff = len(self.listener.content) - self.listener.max_content_len
            del self.listener.content[:diff]

        # Adding the line to the scrolling pad
        if self.listener.scrolling_pad:
            height, width = self.listener.scrolling_pad.getmaxyx()
            if height > 0:
                self.listener.scrolling_pad.addstr(line)
                self.listener.scrolling_pad.noutrefresh()


class LogListener(Listener):
    def __init__(self, title: str, level="DEBUG", log_format="%(asctime)s | %(levelname)-7s | %(name)s: %(message)s"):
        super().__init__(title)

        # Override the robothandler otherwise no output given
        import robot.output.pyloggingconf

        robot.output.pyloggingconf.RobotHandler = Handler

        root_logger = logging.getLogger()
        root_logger.addHandler(Handler(logging.Formatter(log_format).format, self))
        root_logger.setLevel(level)
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
