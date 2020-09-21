from entity.timestamp import Timestamp
from pprint import pformat
from requests import get
from lxml import etree
from re import sub

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
        minor: Flag for minor revision.
        self.index: The 0-indexed position in the revision history.
        
    """
    def __init__(self, revid, parentid, url, user, userid, timestamp, size, text, html, comment, minor, index):
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
            minor: Flag for minor revision.
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
        self.minor = minor
        self.index = index

    def get_html(self):
        """Retrieves HTML via GET request."""
        html = get(self.url + "&oldid=" + str(self.revid)).text
        tree   = etree.HTML(html)
        content = tree.findall("./body/div")[2][4][6][1]
        cleaned_content = etree.tostring(content).decode("utf-8").replace("\n","")
        self.html = sub(r"<!--.*-->","", cleaned_content)

    def serial_timestamp(self):
        return Timestamp(self.timestamp)

    def timestamp_pretty_string(self):
        return self.serial_timestamp().string

    def get_day(self):
        return self.serial_timestamp().datetime.day

    def get_month(self):
        return self.serial_timestamp().datetime.month

    def get_year(self):
        return self.serial_timestamp().datetime.year

    def __str__(self):
        return pformat(self.__dict__)
    
