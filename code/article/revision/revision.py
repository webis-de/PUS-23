from .timestamp import Timestamp
from .source import Source
from .section import Section
from pprint import pformat
from requests import get
from lxml import html, etree
from re import findall, finditer, search, split, sub, S

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
    def __init__(self, revid, parentid, url, user, userid, timestamp, size, html, comment, minor, index, wikitext = ""):
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
            wikitext: The wikitext as provided by the Wikimedia API.
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
        self.timestamp = Timestamp(timestamp)
        self.size = size
        self.wikitext = wikitext
        self.html = html
        self.comment = comment
        self.minor = minor
        self.index = index

    def etree_from_html(self):
        try:
            return html.fromstring(self.html)
        except etree.ParserError:
            return html.fromstring("<html></html>")

    def get_wikitext(self):
        return self.wikitext
        
    def get_text(self):
        try:
            return "".join(self.etree_from_html().xpath(".//div[@class='mw-parser-output']")[0].xpath("//text()")).strip()
        except IndexError:
            return "".join(self.etree_from_html().xpath(".//text()")).strip()

    def get_sections(self):
        #get all sections, i.e. paragraphs, lists, headings, captions, tables
        return self.get_paragraphs() + self.get_lists() + self.get_headings() + self.get_captions() + self.get_tables()

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
        return [Source(source[1]) for source in enumerate(self.etree_from_html().xpath(".//ol[@class='references']/li | .//ol/li/cite"))]

    def get_further_reading(self):
        return [Source(source[1]) for source in enumerate(self.etree_from_html().xpath(".//ul/li/cite"))]

    def get_referenced_authors(self, language, sources):
        return [source.get_authors(language) for source in sources]

    def get_referenced_titles(self, language, source):
        return [source.get_title(language) for source in sources]

    def get_referenced_dois(self, source):
        return [source.get_dois() for source in sources]

    def get_referenced_pmids(self, source):
        return [source.get_pmids() for source in sources]

    def get_lr_contexts(self, keyphrase, width=50, wikitext=False, lower=False, return_keyphrase=False):
        '''
        Generic function to get contexts left and right of keyphrase
        Returns 2-tuple with left and right contexts, 3-tuple including keyphrase if specified by 'return_keyphrase'
        Author: Arno Simons
        '''
        def find_start_indices(text, keyphrase): # https://stackoverflow.com/questions/4664850/how-to-find-all-occurrences-of-a-substring
            ''' 
            Returns start indices for all matches of keyphrase 
            '''
            start = 0
            while True:
              start = text.find(keyphrase, start)
              if start == -1: 
                return
              yield start
              start += len(keyphrase) # use start += 1 to find overlapping matches

        contexts = []
        text = self.get_text() if not wikitext else self.get_wikitext()
        if lower:
            text = text.lower()
        for indx in find_start_indices(text, keyphrase): # use wikitext instead?
            # context left
            left = ''
            for char in text[indx - width : indx][::-1]:
                if char == '\n': # make '\n' the boundary for context
                    break
                left += char
            left = left[::-1].strip()
            # context right
            right = ''
            for char in text[indx + len(keyphrase): indx + len(keyphrase) + width]:
              if char == '\n': # make '\n' the boundary for context
                break
              right += char
            right = right.strip()
            contexts.append((left, right) if not return_keyphrase else (left, keyphrase, right))
        return contexts

    def __str__(self):
        return pformat(self.__dict__)
    
