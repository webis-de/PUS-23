class Revision:
    """
    Wrapper class for revision

    Attributes:
        text: The raw full text of the revision.
        timestamp: The Timestamp object pertaining to the revision.
    """
    def __init__(self, ID, text, timestamp, index):
        """
        Intialises the revision from the revision dictionary entry provided.

        Args:
            revision: The revision as extracted from the revision history.
            index: The 0-indexed position in the revision history.
        """
        self.id = ID
        self.text = text
        self.timestamp = timestamp
        self.index = index
    
