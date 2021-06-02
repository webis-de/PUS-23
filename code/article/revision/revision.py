from .timestamp import Timestamp
from .source import Source
from .section import Section
from pprint import pformat
from lxml import html, etree
from re import findall, finditer, search, split, sub, S

DEFAULT_HTML = ("<div class='mw-parser-output'></div>"
                "<div id='mw-normal-catlinks' class='mw-normal-catlinks'></div>")

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
            return html.fromstring(sub(r"<style.*?</style>", "", self.html, flags=S))
        except etree.ParserError:
            return html.fromstring(DEFAULT_HTML)

    def section_tree(self, name = "root"):
        return Section(self.etree_from_html().find_class('mw-parser-output')[0], name).tree()

    def get_wikitext(self):
        return self.wikitext
    
    def get_text(self):
        return self.etree_from_html()[0].xpath("string()").strip()
        try:
            return "".join(self.etree_from_html().xpath(".//div[@class='mw-parser-output']")[0].xpath("//text()")).strip()
        except IndexError:
            return "".join(self.etree_from_html().xpath(".//text()")).strip()

    def get_headings(self):
        #get all headlines
        return self.section_tree().get_headings()

    def get_paragraphs(self):
        #get all paragraphs
        return self.section_tree().get_paragraphs()

    def get_lists(self):
        #get all ordered lists and unordered lists
        return self.section_tree().get_lists()

    def get_captions(self):
        #get all captions and thumbnails
        return self.section_tree().get_captions()

    def get_tables(self):
        #get all tables
        return self.section_tree().get_tables()

    def get_categories(self):
        return [(element.text, element.get("href")) for element in self.etree_from_html().xpath(".//div[@id='mw-normal-catlinks']//a")[1:]]

    def get_references(self):
        return [Source(source) for source in self.etree_from_html().xpath(".//ol[@class='references']/li | .//ol/li/cite")]

    def get_further_reading(self):
        return [Source(source) for source in self.etree_from_html().xpath(".//ul/li/cite")]

    def get_referenced_authors(self, language, sources):
        return [source.get_authors(language) for source in sources]

    def get_referenced_titles(self, language, sources):
        return [source.get_title(language) for source in sources]

    def get_referenced_dois(self, sources):
        return [source.get_dois() for source in sources]

    def get_referenced_pmids(self, sources):
        return [source.get_pmids() for source in sources]

    def get_lr_contexts(self, keyphrase, width=50, lower=False):
        '''
        Generic function to get contexts left and right of keyphrase
        Returns 2-tuple with left and right contexts, 3-tuple including keyphrase if specified by 'return_keyphrase'
        Author: Arno Simons
        '''
        contexts = []
        keyphrase = keyphrase.strip()
        if keyphrase:
            text = self.get_text() if not lower else self.get_text().lower()
            for start, end in [item.span() for item in finditer(keyphrase, text)]:
                # context left
                left = ''
                for char in text[start - width if not width > start else 0: start][::-1]:
                    if char == '\n': # make '\n' the boundary for context
                        break
                    left += char
                left = left[::-1].strip()
                # context right
                right = ''
                for char in text[end: end + width]:
                  if char == '\n': # make '\n' the boundary for context
                    break
                  right += char
                right = right.strip()
                contexts.append((left, right))
        return contexts

    def __str__(self):
        return pformat(self.__dict__)    
