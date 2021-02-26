from .timestamp import Timestamp
from .source import Source
from .section import Section
from .arno_section import Arno_Section
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

    def tree(self):
        return Section(self.etree_from_html()[0], "root").tree()

    def find(self, text):
        return self.tree.find(text)

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


    def get_arno_sections(self, headline_range = range(1,7)):
        """
        Get the sections of the revision.

        Returns:
            Sections as a list of Arno_Section objects.
        """
        # extract sections in order of appearance and regardless of section level (using regex to cut the html)
        indices = list(finditer(r'|'.join([fr'<h{i}.*?h{i}>' for i in range(1,7)]), self.html))
        starts = [m.start() for m in indices]
        ends = [m.end() for m in indices]
        headings_html = [self.html[start:end] for start, end in zip(starts,ends)]
        texts_html = [self.html[end:start] for end, start in zip(ends, starts[1:])] + [self.html[ends[-1]:]]
        # create lonesome sections
        sections = [Arno_Section(self, heading_html.strip(), text_html.strip()) for heading_html, text_html in zip(headings_html, texts_html)]
        # assign parents, children, next, and previous
        last_parents = [None for i in range(0,10)]
        last_section = None
        for section in sections:
          if last_section:
            last_section.next = section
            if section.level > last_section.level:
              last_section.children.append(section)
              section.parent = last_section
              last_parents[section.level] = section
            elif section.level == last_section.level:
              if last_section.parent:
                section.parent = last_section.parent
                last_section.parent.children.append(section)
              last_parents[section.level] = section
            elif section.level < last_section.level:
              if last_parents[section.level]:
                if last_parents[section.level].parent:
                  section.parent = last_parents[section.level].parent 
                  last_parents[section.level].parent .children.append(section)
            section.previous = last_section
          last_section = section
          last_parents[section.level] = section
        return sections

    def get_specific_sections(self, selection):
        """
        Get specific sections based on a selection of headings.

        Args:
            selection: iterator of strings (each string representing a desired heading)

        Returns:
            Sections as a list of Arno_Section objects.
        """
        return [section for section in self.get_arno_sections() if any(section.heading == heading for heading in selection)]

    def get_section_headings(self, show_parents=True):
        return [section.get_fullheading() if show_parents else section.heading for section in self.get_arno_sections()]

    
