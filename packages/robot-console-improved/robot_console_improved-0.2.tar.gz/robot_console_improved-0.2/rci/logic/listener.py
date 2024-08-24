from rci.representation.sub_window import BorderedWindow


class Listener(BorderedWindow):
    def __init__(self, title: str):
        super().__init__(title)
        self.max_content_len = 50
        self.show_content = True
        self.need_full_redraw = False
