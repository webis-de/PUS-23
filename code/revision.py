class Revision:
    """
    Wrapper class for revision

    Attributes:
        revid: The ID of the revision
        user: The username of the user who penned this revision.
        userid: The user ID of the user who penned this revision.
        timestamp: The Timestamp object pertaining to the revision.
        size: The size of this revision in Bytes.
        text: The raw full text of the revision.
        comment: The comment the user left.
        self.index: The 0-indexed position in the revision history.
        
    """
    def __init__(self, revid, user, userid, timestamp, size, text, comment, index):
        """
        Intialises the revision from the revision dictionary entry provided.

        Args:
            revid: The ID of the revision
            user: The username of the user who penned this revision.
            userid: The user ID of the user who penned this revision.
            timestamp: The Timestamp object pertaining to the revision.
            size: The size of this revision in Bytes.
            text: The raw full text of the revision.
            comment: The comment the user left.
            self.index: The 0-indexed position in the revision history.
        """
        self.revid = revid
        self.user = user
        self.userid = userid
        self.timestamp = timestamp
        self.size = size
        self.text = text
        self.comment = comment
        self.index = index
    
