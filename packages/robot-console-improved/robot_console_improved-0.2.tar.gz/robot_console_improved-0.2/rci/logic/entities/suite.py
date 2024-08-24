from rci.logic.entities.test import Test
from rci.logic.entity import Entity


class Suite(Entity):
    def __init__(self, id: str, name: str, test_count: int):
        super().__init__(id, name)

        self.outer_suite: Suite | None = None
        self.inner_suites: list[Suite] = []
        self.tests: list[Test] = []
        self.test_count = test_count

    def get_succeed_tests(self):
        """
        Counts the number of succeed tests that belong to the suite.
        :return: The number of succeed tests
        """
        return sum(test.status == "PASS" for test in self.tests)

    def get_formatted_string(self, available_columns: int, depth: int = 0, finished: bool = False) -> str:
        """
        Returns a formatted string that fits the terminal
        :param depth: the depth of the string
        :param available_columns: the number of available columns
        :param finished: indicates if all tests are finished
        :return: the formatted string
        """

        if finished:
            overview = (
                f"{self.name} is finished.\n"
                f"{self.get_succeed_tests()}/{self.test_count} tests passed.\n"
                f"Duration {self.get_elapsed_time()}\n"
            )
            return overview

        comp_tests = f"{self.get_succeed_tests()}/{self.test_count}"
        suite_info = f"{comp_tests}    {self.get_elapsed_time()}"

        whitespace = available_columns - len(self.name) - len(suite_info)

        # If there is no space left, only show the name
        if whitespace <= 0:
            return f"{self.name}"

        return f"{self.name}{' ' * whitespace}{suite_info}"
