from rci.logic.entity import Entity


class Keyword(Entity):
    def get_formatted_string(self, available_columns: int, depth: int = 0, finished: bool = False) -> str:
        """
        Returns a formatted string that fits the terminal
        :param depth: the depth of the string
        :param available_columns: the number of available columns
        :param finished: indicates if all tests are finished
        :return: the formatted string
        """

        elp_time = self.get_elapsed_time()

        whitespace = available_columns - depth * 2 - len(self.name) - len(elp_time)

        # If there is no space left, only show the name
        if whitespace <= 0:
            return f"{self.name}"

        return f"{'  ' * depth}{self.name}{' ' * whitespace}{elp_time}"
