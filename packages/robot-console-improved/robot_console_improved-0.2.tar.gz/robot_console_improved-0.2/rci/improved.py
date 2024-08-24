from robot.output.loggerapi import LoggerApi

from rci.logic.listeners.console_listener import ConsoleListener
from rci.logic.listeners.execution_listener import ExecutionListener
from rci.logic.listeners.keyword_listener import KeywordListener
from rci.logic.listeners.log_listener import LogListener
from rci.representation.interface import Interface


class Improved(LoggerApi):
    def __init__(self, width=78, colors='AUTO', markers='AUTO', stdout=None, stderr=None):
        # Initialize the listeners
        self.execution_listener: ExecutionListener = ExecutionListener("Test Execution")
        self.keyword_listener: KeywordListener = KeywordListener("Keyword Execution")
        self.log_listener: LogListener = LogListener("Logs")
        self.console_listener: ConsoleListener = ConsoleListener("Console")

        self.interface: Interface = Interface()

        # Add the listeners to the interface
        self.interface.add_listener(self.execution_listener)
        self.interface.add_listener(self.keyword_listener)
        self.interface.add_listener(self.log_listener)
        self.interface.add_listener(self.console_listener)

        if not self.interface.create_windows():
            self.interface.resize_message()

        # Starting the interface
        self.interface.start_interface()

    def start_suite(self, data, result):
        """
        Will be called every time a test suite starts
        :param suite: represents the test suite
        :return:
        """
        self.execution_listener.start_suite(data)

    def end_suite(self, data, result):
        """
        Will be called every time a test suite ends
        :param suite: represents the test suite
        """

        self.execution_listener.end_suite(data)

    def start_test(self, data, result):
        """
        Will be called every time a test starts
        :param test: represents the test
        """
        self.execution_listener.start_test(data)

    def end_test(self, data, result):
        """
        Will be called every time a test ends
        :param test: represents the test
        """
        if result.failed:
            self.console_listener.write(f"\n{result.message}")

        self.execution_listener.end_test(result)

    def start_keyword(self, data, result):
        """
        Will be called every time a keyword starts
        :param kw: represents the keyword
        """
        self.keyword_listener.start_keyword(data)

    def end_keyword(self, data, result):
        """
        Will be called every time a keyword ends
        :param kw: represents the keyword
        """
        self.keyword_listener.end_keyword(data)

    def message(self, msg):
        pass

    def log_message(self, msg):
        pass

    def imported(self, import_type, name, attrs):
        pass

    def output_file(self, path):
        pass

    def log_file(self, path):
        pass

    def report_file(self, path):
        pass

    def close(self):
        """
        Will be called when the execution is finished
        """

        # Draw the last state on the screen, and print out an exit message
        self.execution_listener.draw_last_state()
        self.console_listener.write("\nPress 'q' to close the window.")
        self.interface.exit()
