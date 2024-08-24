import curses

from rci.representation.sub_window import TextBoxWindow

SUPPORT_DEBUG = True

try:
    import DebugLibrary
except Exception as e:  # no cov
    SUPPORT_DEBUG = False


class InputListener(TextBoxWindow):
    def __init__(self, main_window: curses.window):
        super().__init__(main_window)

        # Overwrite the debug function from DebugLibrary.keywords.DebugKeywords
        DebugLibrary.keywords.DebugCmd.get_input = self.get_input

    @staticmethod
    def convert_enter(keystroke):
        """
        Converts the enter keystroke to BEL, BEL is used to stop the input
        :param keystroke: the keystroke
        :return: the converted keystroke or the original one
        """

        # 10 is the enter keystroke
        if keystroke == 10:
            keystroke = curses.ascii.BEL

        return keystroke

    def get_input(self):
        """
        Overwrites the get_input function from DebugLibrary.keywords.DebugCmd
        :return: the command that was entered
        """

        # Set the cursor visible
        curses.curs_set(1)

        # Set the validator and get the input
        self.text_box.edit(validate=self.convert_enter)

        # Removing the last two characters, which are space and \n
        command = self.text_box.gather()[:-2]

        # Clear the input box
        self.text_box.win.clear()
        self.text_box.win.refresh()

        # Set the cursor invisible
        curses.curs_set(0)

        return command
