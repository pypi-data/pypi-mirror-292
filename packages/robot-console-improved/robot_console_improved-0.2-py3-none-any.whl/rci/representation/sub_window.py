import curses
from abc import abstractmethod
from curses.textpad import Textbox


class SubWindow:
    def __init__(self):
        self.main_window: curses.window | None = None
        self.x = 0
        self.active = True
        self.min_columns = 3
        self.min_lines = 3

    @abstractmethod
    def create_display(self, lines: int, cols: int, offset: int) -> bool:
        """
        Creates the display of the sub window that will contain the content.
        :param lines: the number of lines
        :param cols: the number of columns
        :param offset: the offset of the sub window
        :return: True if the sub window was created, otherwise False
        """
        pass

    @abstractmethod
    def update_content(self):
        """
        Updates the content of the sub window
        """
        pass

    def check_dimensions(self, lines: int, columns: int, offset: int, extra_columns: int = 0) -> bool:
        """
        Checks if the dimensions are valid
        :param lines: the number of lines
        :param columns: the number of columns
        :param offset: the offset of the sub window
        :param extra_columns: the number of extra columns
        :return: True if the dimensions are valid, otherwise False
        """

        return (
            lines >= self.min_lines
            and self.min_columns + extra_columns <= columns <= self.main_window.getmaxyx()[1]
            and offset + lines <= self.main_window.getmaxyx()[0]
        )


class BorderedWindow(SubWindow):
    def __init__(self, title: str):
        super().__init__()
        self.title = title
        self.scrolling_pad: curses.window | None = None

    def create_display(self, lines: int, cols: int, offset: int) -> bool:
        """
        Creates the display of the sub window that will contain the content.
        :param lines: the number of lines
        :param cols: the number of columns
        :param offset: the offset of the sub window
        :return: True if the sub window was created, otherwise False
        """

        # checks if the dimensions are valid
        if not self.check_dimensions(lines, cols, offset, len(self.title)):
            return False

        width = cols - 2
        height = lines - 2

        # creates a bordered window, with the given dimensions
        win: curses.window = self.main_window.subwin(lines, cols, offset, self.x)
        win.border()

        # Adds the title
        title = f" {self.title} "
        win.addstr(0, (cols - len(title)) // 2, title)

        # creates the scrolling pad
        # +1 offset because the scrolling pad starts after the border
        self.scrolling_pad = win.subpad(height, width, offset + 1, self.x + 1)
        # enables the scrolling pad to be scrolled
        self.scrolling_pad.scrollok(True)

        return True

    @abstractmethod
    def redraw_content(self):
        """
        Updates the window content after resizing the screen
        """

        pass


class TextBoxWindow(SubWindow):
    def __init__(self, main_window: curses.window):
        super().__init__()
        self.text_box: Textbox | None = None
        self.main_window = main_window
        self.debug_symbol = ">> "

    def create_display(self, lines: int, cols: int, offset: int) -> bool:
        """
        Creates the display of the sub window that will contain the content.
        :param lines: the number of lines
        :param cols: the number of columns
        :param offset: the offset of the sub window
        :return: True if the sub window was created, otherwise False
        """

        # checks if the dimensions are valid
        if not self.check_dimensions(lines, cols, offset, len(self.debug_symbol)):
            return False

        width = cols - 2
        height = lines - 2

        # creates a bordered window, with the given dimensions
        win: curses.window = self.main_window.subwin(lines, cols, offset, self.x)
        win.border()

        # Add a prefix, which indicates the startpoint for typing in the text box
        # starting with an offset of 1, because of the border
        win.addstr(1, 1, self.debug_symbol)

        # Creates the text box
        # the bigger offsets because of the prefix
        pad: curses.window = win.subpad(height, width - len(self.debug_symbol), offset + 1, self.x + 1 + len(self.debug_symbol))
        self.text_box = Textbox(pad)

        return True
