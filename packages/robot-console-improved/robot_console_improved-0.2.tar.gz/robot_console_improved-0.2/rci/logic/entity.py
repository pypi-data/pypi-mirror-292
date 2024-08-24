import datetime
import time
from abc import abstractmethod


class Entity:
    def __init__(self, id: str, name: str):
        self.id = id
        self.name = name
        self.start_time: datetime.datetime = datetime.datetime.now()
        self.elapsed_time: str | None = None
        self.is_finished = False

    def get_elapsed_time(self) -> str:
        """
        Returns the elapsed time of the current suite in seconds, minutes or hours, depending on the time.
        :return: the elapsed time
        """

        if self.elapsed_time is not None:
            return self.elapsed_time

        cur_time = datetime.datetime.now()
        elp_time_sec = (cur_time - self.start_time).total_seconds()
        return time.strftime("%H:%M:%S", time.gmtime(elp_time_sec))

    def done(self):
        """
        Sets the end time of the entity to the current time.
        """
        self.is_finished = True
        self.elapsed_time = self.get_elapsed_time()

    @abstractmethod
    def get_formatted_string(self, available_columns: int, depth: int = 0, finished: bool = False) -> str:
        """
        Returns a formatted string that fits the terminal
        :param depth: the depth of the string
        :param available_columns: the number of available columns
        :param finished: indicates if all tests are finished
        :return: the formatted string
        """
        pass
