from robot.result import Keyword

from rci.logic.entities.keyword import Keyword as RciKeyword
from rci.logic.listener import Listener


class KeywordListener(Listener):
    def __init__(self, title: str):
        super().__init__(title)
        self.keywords_stack: list[RciKeyword] = []

        self.need_full_redraw = True

    def start_keyword(self, kw: Keyword):
        """
        Called when a keyword or a control structure such as IF/ELSE or TRY/EXCEPT starts.
        :param kw: the keyword that starts.
        """

        if kw.type == 'IF/ELSE ROOT':
            return

        # If the keyword already in the stack, don't add it anymore
        for keyword in self.keywords_stack:
            if keyword.id == kw.id:
                return

        # Creating a new keyword and add it to the stack
        new_keyword: RciKeyword = RciKeyword(kw.id, str(kw))

        self.keywords_stack.append(new_keyword)

    def end_keyword(self, kw: Keyword):
        """
        Called when a keyword ends.
        :param kw: the keyword that ends.
        """

        if kw.type == 'IF/ELSE ROOT':
            return

        # If the keyword with the id is not in the stack, return
        # This can happen because sometimes it wants to add the same keyword 2 times, so we prevent that
        # But than we need to do a check here, so we don't pop a wrong keyword
        for keyword in self.keywords_stack:
            if keyword.id == kw.id:
                break
        else:
            return

        # The keyword closes, so we pop it from the stack
        closed_keyword = self.keywords_stack.pop()

        # Check if the popped keyword matches the ended keyword by robot
        assert closed_keyword.id == kw.id, "Internal error, please restart."

    def redraw_content(self):
        """
        Updates the window content after resizing the screen
        :return:
        """

        if self.scrolling_pad is None:
            return

        # Clearing the scrolling pad content
        self.scrolling_pad.clear()

        if not self.show_content:
            return

        # Getting the width and height of the scrolling pad
        height, width = self.scrolling_pad.getmaxyx()

        # If the height is 0, there is nothing to display
        if height == 0:
            return

        # Getting the keywords to display
        available_kws: list[RciKeyword] = self.keywords_stack[-height::]

        # Creating a string with the overview of the keywords
        overview = ''.join(kw.get_formatted_string(width, i) for i, kw in enumerate(available_kws))

        # Adding the overview to the scrolling pad
        self.scrolling_pad.addstr(0, 0, overview)
        self.scrolling_pad.noutrefresh()
