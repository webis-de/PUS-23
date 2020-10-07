from entity.timestamp import Timestamp
from entity.page import Page
from pprint import pformat
from requests import get
from lxml import html
from re import finditer, split, sub, S

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
        html: The HTML of this revision.
        comment: The comment the user left.
        minor: Flag for minor revision.
        self.index: The 0-indexed position in the revision history.
        
    """
    def __init__(self, revid, parentid, url, user, userid, timestamp, size, html, comment, minor, index):
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
        self.html = html
        self.comment = comment
        self.minor = minor
        self.index = index

    def request_html(self):
        """
        Retrieves HTML via GET request.

        Returns:
            revid if mw-parser-output does not exist (revision removed), else None.
        """
        revision_url = self.url + "&oldid=" + str(self.revid)
        page = Page(str(self.revid), revision_url)
        self.html = page.get_mediawiki_parser_output_and_normal_catlinks()
        if not self.html:
            return self.revid
        else:
            return None
        
    def get_text(self):
        self.tree = html.fromstring(self.html)
        try:
            return "".join(self.tree.xpath(".//div[@class='mw-parser-output']")[0].itertext())
        except IndexError:
            return ""

    def get_categories(self):
        self.tree = html.fromstring(self.html)
        return [(element.text, element.get("href")) for element in self.tree.xpath(".//div[@id='mw-normal-catlinks']//a")[1:]]

    def get_references(self):
        self.tree = html.fromstring(self.html)
        return self.tree.xpath(".//div[@class='mw-parser-output']//span[@class='reference-text']")

    def get_referenced_authors(self):
        authors = []
        for reference in self.get_references():
            text =  "".join(reference.itertext())
            AUTHORS = []
            if "(" in text:
                #remove everything after first (
                text = sub(r"\(.*", "", text)
                #remove et al.
                text = sub(r",? *et al\.?", "", text).strip()
                #get surnames and fist names
                for author in split(r", ?", text):
                    try:
                        match = next(finditer(r".* ", author))
                        AUTHORS.append((author[0:match.end()-1], author[match.end():]))
                    except StopIteration:
                        pass
            authors.append(AUTHORS)
        return authors

    def get_referenced_titles(self):
        titles = []
        for reference in self.get_references():
            try:
                #get full text of reference
                text = "".join(reference.itertext())
                #split at year
                text = split(r"\([a-zA-Z]* ?\d+\)\.? ?", text, 1)[1].strip()
                try:
                    #try to find quoted title
                    match = next(finditer(r"\".*\"", text))
                    #get span of first match
                    text = text[match.start():match.end()]
                    #remove quotation marks
                    title = text.replace("\"", "")
                except StopIteration:
                    #split at stop
                    text = text.split(".")[0]
                    #remove quotation marks
                    title = text.replace("\"", "")
                titles.append(title)
            except IndexError:
                titles.append("")
        return titles

    def get_referenced_dois(self):
        dois = []
        for reference in self.get_references():
            DOIs = []
            for element in reference.xpath(".//a[contains(@href, 'doi.org/')]"):
                #dois from links
                DOIs.append(element.attrib["href"].split("doi.org/")[-1].replace("%2F","/"))
                #dois from element text
                DOIs.append(element.text)
            dois.append([doi for doi in list(set(DOIs)) if " " not in doi])
        return dois

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
    
