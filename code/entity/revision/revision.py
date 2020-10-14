from entity.timestamp import Timestamp
from .reference import Reference
from .section import Section
from pprint import pformat
from requests import get
from lxml import html, etree
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

    def etree_from_html(self):
        try:
            return html.fromstring(self.html)
        except etree.ParserError:
            return html.fromstring("<html></html>")
        
    def get_text(self):
        try:
            return "".join(self.etree_from_html().xpath(".//div[@class='mw-parser-output']")[0].xpath("//text()")).strip()
        except IndexError:
            return "".join(self.etree_from_html().xpath(".//text()")).strip()

    def get_paragraphs(self):
        #get all unclassified paragraphs
        xpath_expression = "./p[not(@class)]"
        try:
            return [Section(section) for section in self.etree_from_html().xpath(".//div[@class='mw-parser-output']")[0].xpath(xpath_expression)]
        except IndexError:
            return [Section(section) for section in self.etree_from_html().xpath(xpath_expression)]

    def get_lists(self):
        #get all ordered lists and unordered lists
        xpath_expression = "|".join(["./" + tag + "[not(@class)]" for tag in ["ol","ul"]])
        try:
            return [Section(section) for section in self.etree_from_html().xpath(".//div[@class='mw-parser-output']")[0].xpath(xpath_expression)]
        except IndexError:
            return [Section(section) for section in self.etree_from_html().xpath(xpath_expression)]

    def get_headings(self):
        #get all headlines
        xpath_expression = "|".join(["./" + tag + "[not(@class)]" for tag in ["h1","h2","h3","h4","h5","h6"]])
        try:
            return [Section(section) for section in self.etree_from_html().xpath(".//div[@class='mw-parser-output']")[0].xpath(xpath_expression)]
        except IndexError:
            return [Section(section) for section in self.etree_from_html().xpath(xpath_expression)]

    def get_captions(self):
        #get all captions and thumbnails
        xpath_expression = ".//div[@class='thumbcaption']"
        try:
            return [Section(section) for section in self.etree_from_html().xpath(".//div[@class='mw-parser-output']")[0].xpath(xpath_expression)]
        except IndexError:
            return [Section(section) for section in self.etree_from_html().xpath(xpath_expression)]

    def get_tables(self):
        #get all tables
        xpath_expression = ".//table"
        try:
            return [Section(section) for section in self.etree_from_html().xpath(".//div[@class='mw-parser-output']")[0].xpath(xpath_expression)]
        except IndexError:
            return [Section(section) for section in self.etree_from_html().xpath(xpath_expression)]

    def get_categories(self):
        return [(element.text, element.get("href")) for element in self.etree_from_html().xpath(".//div[@id='mw-normal-catlinks']//a")[1:]]

    def get_references(self):
        return [Reference(reference[1], reference[0] + 1) for reference in enumerate(self.etree_from_html().xpath(".//ol[@class='references']/li | .//ol/li/cite"))]

    def get_further_reading(self):
        return [Reference(reference[1], None) for reference in enumerate(self.etree_from_html().xpath(".//ul/li/cite"))]

    def get_referenced_authors(self, language, source):
        authors = []
        for reference in source:
            if language == "en":
                #get full text of reference
                text = reference.text()
                AUTHORS = []
                if "(" in text:
                    #remove everything after first (
                    text = sub(r"\(.*", "", text)
                    #remove et al.
                    text = sub(r",? *et al\.?", "", text).strip()
                    #get surnames and fistnames
                    for author in split(r", ?", text):
                        try:
                            match = next(finditer(r".* ", author))
                            AUTHORS.append((author[0:match.end()-1], author[match.end():]))
                        except StopIteration:
                            pass
                authors.append(AUTHORS)
            if language == "de":
                #get full text of reference
                text = reference.text()
                AUTHORS = []
                try:
                    #split at :
                    text = text.split(":")[0]
                    #remove et al.
                    text = sub(r",? *et al\.?", "", text).strip()
                    #get surnames and fist names
                    for author in split(r", ?", text):
                        try:
                            match = next(finditer(r".*\. ", author))
                            AUTHORS.append((author[match.end():], author[0:match.end()-1]))
                        except StopIteration:
                            pass
                except IndexError:
                    pass
                authors.append(AUTHORS)
        return authors

    def get_referenced_titles(self, language, source):
        titles = []
        for reference in source:
            if language == "en":
                try:
                    #get full text of reference
                    text = reference.text()
                    #split at year
                    text = split(r"\(.*?\)\.? ?", text, 1)[1].strip()
                    try:
                        #try to find quoted title
                        match = next(finditer(r"\".*?\"", text))
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
            if language == "de":
                #get full text of reference
                text = reference.text()
                try:
                    #split at :
                    text = split(":", text, 1)[1].strip()
                    #split at .
                    title = text.split(".")[0].strip()
                    
                    titles.append(title)
                except IndexError:
                    titles.append("")  
        return titles

    def get_referenced_dois(self, source):
        dois = []
        for reference in source:
            DOIs = []
            for element in reference.source.xpath(".//a[contains(@href, 'doi.org/')]"):
                #dois from links
                DOIs.append(element.get("href").split("doi.org/")[-1].replace("%2F","/"))
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
    
