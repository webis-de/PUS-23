from datetime import datetime
from pprint import pformat

class Timestamp:
    """
    Wrapper class for timestamp.

    Attributes:
        datetime: Timestamp as datetime object.
        string: Timestamp as string.
        index: Timestamp as 0-indexed position in revision history.
    """    
    
    def __init__(self, timestamp_string, index):
        """
        Initialises the timestamp.

        Args:
            timestamp_string: Timestamp as string as extracted from revision history.
            index: Timestamp as 0-indexed position in revision history.
        """

        self.datetime = datetime.strptime(timestamp_string, "%Y-%m-%dT%H:%M:%SZ")
        self.string = str(self.datetime)
        self.index = index

    def __str__(self):
        return pformat(self.__dict__)

if __name__ == "__main__":

    timestamp = Timestamp("2020-7-6T17:10:20Z", 42)
    print(timestamp)
