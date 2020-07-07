from timestamp import Timestamp

class Revision:
    """
    Wrapper class for revision

    Attributes:
        text: The raw full text of the revision.
        timestamp: The Timestamp object pertaining to the revision.
    """
    def __init__(self, revision, index):
        """
        Intialises the revision from the revision dictionary entry provided.

        Args:
            revision: The revision as extracted from the revision history.
            index: The 0-indexed position in the revision history.
        """
        try:
            self.text = revision["text"]["#text"]
        except:
            self.text = ""
        self.timestamp = Timestamp(revision["timestamp"], index)
    
