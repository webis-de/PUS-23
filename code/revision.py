from pprint import pformat
from requests import get

class Revision:
    """
    Wrapper class for revision

    Attributes:
        revid: The ID of the revision
        parentid: The ID of the previsious revision; 0 if none.
        url: The url of this revision.
        user: The username of the user who penned this revision.
        userid: The user ID of the user who penned this revision.
        timestamp: The Timestamp object pertaining to the revision.
        size: The size of this revision in Bytes.
        text: The raw full text of the revision.
        html: The HTML of this revision.
        comment: The comment the user left.
        self.index: The 0-indexed position in the revision history.
        
    """
    def __init__(self, revid, parentid, url, user, userid, timestamp, size, text, html, comment, index):
        """
        Intialises the revision from the revision dictionary entry provided.

        Args:
            revid: The ID of the revision
            parentid: The ID of the previsious revision; 0 if none.
            url: The url of this revision.
            user: The username of the user who penned this revision.
            userid: The user ID of the user who penned this revision.
            timestamp: The Timestamp object pertaining to the revision.
            size: The size of this revision in Bytes.
            text: The raw full text of the revision.
            html: The HTML of this revision.
            comment: The comment the user left.
            index: The 0-indexed position in the revision history.
        """
        self.revid = revid
        self.parentid = parentid
        self.url = url
        self.user = user
        self.userid = userid
        self.timestamp = timestamp
        self.size = size
        self.text = text
        self.html = html
        self.comment = comment
        self.index = index

    def get_html(self):
        """Retrieves HTML via GET request."""
        self.html = get(self.url + "&oldid=" + str(self.revid)).text[:20]

    def __str__(self):
        return pformat(self.__dict__)
    
