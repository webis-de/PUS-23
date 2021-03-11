from re import sub
from lxml import html as HTML
from queue import Queue
from copy import deepcopy

class Section:

    def __init__(self, html, name = "root", parent = None, level = 0):

        self.html = html
        self.name = name
        self.parent = parent
        self.prev = None
        self.next = None
        self.level = level
        self.subsections = []

    def get_text(self, level = 0, include = ["p","li"], with_headings = False):
        """
        Get the text of this section.

        Args:
            level: The depth to which text from subsections will be retrieved.
            include: List of HTML element tags to include.
            exclude: List of HTML element tags to exclude.
            with_headings: Append heading of section to start of string.
        Returns:
            The text of the section a string cleaned of superflous spaces and line breaks.
        """
        text = "\n\n".join([sub(r" +", " ", element.xpath("string()").replace("\n", ""))
                            for element in self.html.iter(include)])
        heading = (self.name + ("\n\n" if text else "")) * with_headings
        if level != 0:
            return heading + text + "\n\n" + "".join([subsection.get_text(level - 1, include, with_headings) for subsection in self.subsections])
        else:
            return heading + text
           
    def get_wikilinks(self, level = 0): # Analog zu get_references (Arno) 
        """
        Get wikilinks in the section.

        Args:
            level: The depth to which wikilinks from subsections will be retrieved.
        Returns:
            A list of wikilinks as strings.
        """
        def recursive_get_wikilinks(section, level, wikilinks):
            wikilinks += [element.get("href") for element in section.html.iter() if element.get("href") and element.get("href").startswith("/wiki/")]
            if level != 0:
                for subsection in section.subsections:
                    recursive_get_wikilinks(subsection, level - 1, wikilinks)
            return wikilinks
        return recursive_get_wikilinks(self, level, [])
        
    def get_reference_ids(self, level = 0):
        """
        Get reference ids in the section.

        Args:
            level: The depth to which reference ids from subsections will be retrieved.
        Returns:
            A list of reference ids as strings.
        """
        def recursive_get_reference_ids(section, level, reference_ids):
            reference_ids += [element.get("id") for element in section.html.iter() if element.get("class") == "reference"]
            if level != 0:
                for subsection in section.subsections:
                    recursive_get_reference_ids(subsection, level - 1, reference_ids)
            return reference_ids
        return recursive_get_reference_ids(self, level, [])

    def get_sources(self, sources, level = 0):
        """
        Get all sources referenced in this section.

        Args:
            sources: The sources which will be matched against this section.
            level: The depth to which sources from subsections will be retrieved.
        Returns:
            A list of sources.
        """
        referenced_ids_in_section = set(self.get_reference_ids(level))
        return [source for source in sources
                if not set(source.get_reference_ids()).isdisjoint(referenced_ids_in_section)]     

    def tree(self, headings = ["h1","h2","h3","h4","h5","h6"]):
        """
        Creates a nested section tree from this section.

        Returns:
            A section tree of headings, paragraphs and divs.
        """
        html = deepcopy(self.html)
        self.html.clear()
        heading_level = 0
        for element in html:
            if not heading_level and element.tag in headings:
                heading_level = headings.index(element.tag) + 1
            if element.tag not in headings[:max(heading_level,0)]:
                if not self.subsections:
                    self.html.append(element)
                else:
                    self.subsections[-1].append(element)
            else:
                self.subsections.append(HTML.fromstring('<div class="section"></div>'))
                self.subsections[-1].append(element)
        self.subsections = [self._html_to_section(html, headings[max(heading_level,0):]) for html in self.subsections]
        self._siblings()
        return self

    def _html_to_section(self, html, headings):
        """
        Turns a list of elements into a new subsection and calls tree on it.

        Args:
            elements: A list of HTML elements.
            name: The name of the subsection.
            level: The level of this subsection.
        """
        if html is not None:
            name = html[0].xpath("string()").split('[edit]')[0].strip()
            subsection = Section(html, name, self, self.level + 1)
            subsection.tree(headings)
            return subsection

    def _siblings(self):
        for subsection1,subsection2 in zip(self.subsections[:-1], self.subsections[1:]):
            subsection1.next = subsection2
            subsection2.prev = subsection1
        for subsection in self.subsections:
            subsection._siblings()

    def find(self, strings, lower = False):
        """
        Recursively finds all subsections in the section tree with any of the given strings in the title.

        Args:
            strings: A list of strings to search in the title.
        Returns:
            A list of sections.
        """
        def recursive_find(section, strings, lower, sections):
            for subsection in section.subsections:
                for string in [(string.lower() if lower else string) for string in strings]:
                    if string in (subsection.name.lower() if lower else subsection.name):
                        sections.append(subsection)
                        break
                recursive_find(subsection, strings, lower, sections)
            return sections
        return recursive_find(self, strings, lower, [self] if any([string in self.name for string in strings]) else [])

    def get_paragraphs(self):
        def recursive_get_paragraphs(section, paragraphs):
            paragraphs += [element for element in section.html.iter(["p"])]
            for subsection in section.subsections:
                recursive_get_paragraphs(subsection, paragraphs)
            return paragraphs
        return recursive_get_paragraphs(self, [])

    def get_headings(self):
        def recursive_get_paragraphs(section, headings):
            headings += [element for element in section.html.iter(["h2","h3","h4","h5","h6"])]
            for subsection in section.subsections:
                recursive_get_paragraphs(subsection, headings)
            return headings
        return recursive_get_paragraphs(self, [])

    def get_lists(self):
        def recursive_get_lists(section, lists):
            lists += [element for element in section.html.iter(["ol","ul"])]
            for subsection in section.subsections:
                recursive_get_lists(subsection, lists)
            return lists
        return recursive_get_lists(self, [])

    def get_tables(self):
        def recursive_get_tables(section, tables):
            tables += [element for element in section.html.iter(["table"])]
            for subsection in section.subsections:
                recursive_get_tables(subsection, tables)
            return tables
        return recursive_get_tables(self, [])

    def get_captions(self):
        def recursive_get_captions(section, captions):
            captions += [element for element in section.html.iter() if element.get("class") == "thumbcaption"]
            for subsection in section.subsections:
                recursive_get_captions(subsection, captions)
            return captions
        return recursive_get_captions(self, [])

    def parent_path(self):
        """
        Get the path of parent names.

        Returns:
            The pipe-separated path to this section.
        """
        if not self.parent:
            return self.name
        else:
            return self.parent.parent_path() + "|" + self.name

    def parent_name(self):
        """
        Get the parent name.

        Returns:
            The name of the parent; None if root.
        """
        return self.parent.name if self.parent else None

    def json(self):
        """
        Return this section as a json object.

        Returns:
            This section as a dictionary.
        """
        return {"name":self.name,
                "level":self.level,
                "parent":self.parent_name(),
                "path":self.parent_path(),
                "text":self.get_text(),
                "subsections":[subsection.json() for subsection in self.subsections]}
