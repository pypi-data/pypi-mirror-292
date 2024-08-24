from rci.logic.entity import Entity


class Test(Entity):
    def __init__(self, id: str, name: str, timeout: str | None = None):
        super().__init__(id, name)

        self.timeout = str(timeout) if timeout is not None else "∞"
        self.status = 'FAIL'

    def get_formatted_string(self, available_columns: int, depth: int = 0, finished: bool = False) -> str:
        """
        Returns a formatted string that fits the terminal
        :param depth: the depth of the string
        :param available_columns: the number of available columns
        :param finished: indicates if all tests are finished
        :return: the formatted string
        """

        info = self.status if self.is_finished else self.timeout
        test_info = f"{info}    {self.get_elapsed_time()}"
        # Offset of 2 because of the borders
        whitespace = available_columns - len(self.name) - len(test_info)

        # If there is no space left, only show the name
        if whitespace <= 0:
            return f"{self.name}"

        return f"{self.name}{' ' * whitespace}{test_info}"
