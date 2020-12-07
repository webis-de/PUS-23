from datetime import datetime
from pprint import pformat

class Timestamp:
    """
    Wrapper class for timestamp.

    Attributes:
        datetime: Timestamp as datetime object.
        year: The year of the timestamp.
        month: The month of the timestamp.
        day: The day of the timestamp.
        hour: The hour of the timestamp.
        minute: The minute of the timestamp.
        second: The second of the timestamp.
        string: Timestamp as string.
    """    
    
    def __init__(self, timestamp_string):
        """
        Initialises the timestamp.

        Args:
            timestamp_string: Timestamp as string as extracted from revision history.
        """

        self.datetime = datetime.strptime(timestamp_string, "%Y-%m-%dT%H:%M:%SZ")
        self.year = self.datetime.year
        self.month = self.datetime.month
        self.day = self.datetime.day
        self.hour = self.datetime.hour
        self.minute = self.datetime.minute
        self.second = self.datetime.second
        self.string = str(self.datetime)

    def __str__(self):
        return pformat(self.__dict__)


