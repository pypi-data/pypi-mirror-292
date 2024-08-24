from robot.result import TestCase, TestSuite

from rci.logic.entities.suite import Suite
from rci.logic.entities.test import Test
from rci.logic.entity import Entity
from rci.logic.listener import Listener


class ExecutionListener(Listener):
    def __init__(self, title: str):
        super().__init__(title)
        self.suite_stack: list[Suite] = []
        self.test_stack: list[Test] = []

        self.last_popped: Suite | None = None

        self.finished_tests: list[Test] = []

        self.need_full_redraw = True

    def start_suite(self, suite: TestSuite):
        """
        Will be called every time a test suite starts and add it to the stack
        :param suite: Represents a single executable test suite.
        """

        # Create new suite
        new_suite: Suite = Suite(suite.id, suite.name, suite.test_count)

        # There is an active suite, so add it as an inner suite to the active suite
        if len(self.suite_stack) > 0:
            active_suite: Suite = self.suite_stack[-1]
            new_suite.outer_suite = active_suite
            active_suite.inner_suites.append(new_suite)

        # Add the new suite to the stack
        self.suite_stack.append(new_suite)

    def end_suite(self, suite: TestSuite):
        """
        Will be called every time a test suite ends and removes it from the stack
        :param suite: Represents a single executable test suite.
        """

        # The suite closes, so we pop it from the stack
        closed_suite: Suite = self.suite_stack.pop()

        self.last_popped: Suite = closed_suite

        assert suite.id == closed_suite.id, "Internal error, please restart."

        closed_suite.done()

        # Check if suite has an outer suite
        if closed_suite.outer_suite is not None:
            # Add tests to the outer suite tests
            closed_suite.outer_suite.tests.extend(closed_suite.tests)

    def start_test(self, test: TestCase):
        """
        Will be called when a test case starts and add it to the stack.
        :param test: Represents a results of a single test case.
        :return:
        """

        # Create new test and add it to the test stack
        new_test: Test = Test(test.id, test.name, test.timeout)

        # Check for that there is active suite
        if len(self.suite_stack) > 0:
            self.test_stack.append(new_test)

            # Add the test to the current active suite
            active_suite: Suite = self.suite_stack[-1]
            active_suite.tests.append(new_test)

    def end_test(self, test: TestCase):
        """
        Will be called when a test case ens and removes it from the stack.
        :param test: Represents a results of a single test case.
        :return:
        """

        # The tests closes, so we pop it of the stack
        closed_test: Test = self.test_stack.pop()

        assert test.id == closed_test.id, "Internal error, please restart."

        # Update the test status
        closed_test.status = test.status
        closed_test.done()
        self.finished_tests.append(closed_test)

        # If the list is bigger than max content len, delete the first x items
        if len(self.finished_tests) > self.max_content_len:
            diff = len(self.finished_tests) - self.max_content_len
            del self.finished_tests[:diff]

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

        # If there are no suites and no suite is ended, there is nothing to display
        # Or if the height is 0, there cannot be anything displayed
        if (len(self.suite_stack) == 0 and self.last_popped is None) or height == 0 or len(self.suite_stack) == 0:
            return

        # Adding the suites and test to the overview
        overview: list[Entity] = [self.suite_stack[0]]

        # adding the current suite to the overview if there is enough space
        if height > 1:
            overview.append(self.suite_stack[-1])

        # Adding the current test, if there is one
        if len(self.test_stack) > 0 and height > 2:
            overview.append(self.test_stack[-1])

        # Adding the finished tests to the overview, in reverse order
        if height - len(overview) > 0:
            overview.extend(self.finished_tests[-(height - len(overview)) :][::-1])

        stringed_overview = ''.join(entity.get_formatted_string(width) for entity in overview)

        # Adding the overview to the scrolling pad
        self.scrolling_pad.addstr(0, 0, stringed_overview)

        # Adding the new content to the scrolling pad
        self.scrolling_pad.noutrefresh()

    def draw_last_state(self):
        """
        Draws the final state of all the executions on the screen
        :return:
        """

        if not self.scrolling_pad:
            return

        self.scrolling_pad.clear()

        if self.last_popped is None or not self.show_content:
            return

        # Getting the width and height of the scrolling pad
        height, width = self.scrolling_pad.getmaxyx()

        overview: list[Entity] = [self.last_popped]

        # Checking if the height is big enough to add finished tests
        # We take 2 because the newline the formatted string adds, if we take 1, the root suite will not be displayed
        # This is because the overview string is too long and scrolls out of the screen
        if height > 2:
            overview.extend(self.finished_tests[-(height - 2) :][::-1])

        stringed_overview = ''.join(entity.get_formatted_string(width) for entity in overview)

        # Adding the overview to the scrolling pad
        self.scrolling_pad.addstr(0, 0, stringed_overview)

        # Adding the new content to the scrolling pad
        self.scrolling_pad.noutrefresh()
