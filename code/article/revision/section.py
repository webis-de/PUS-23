from re import sub
from lxml import html as HTML
from queue import Queue
from copy import deepcopy

class Section:

    def __init__(self, html, name = "root", parent = None, level = 0, headings = ["h2","h3","h4","h5","h6"]):

        self.html = html
        self.name = name
        self.parent = parent
        self.prev = None
        self.next = None
        self.level = level
        self.subsections = []
        self.headings = headings

    def get_text(self, level = 0, include = ["p","li"], exclude = ["style"], include_heading = False):
        """
        Get the text of this section.

        Args:
            level: The depth to which text from subsections will be retrieved.
            include: List of HTML element tags to include.
            exclude: List of HTML element tags to exclude.
            include_heading: Append heading of section to start of string.
        Returns:
            The text of the section a string cleaned of superflous spaces and line breaks.
        """
        heading = (self.name + "\n\n") * include_heading
        text = "\n\n".join([sub(r" +", " ", element.xpath("string()").replace("\n", ""))
                            for element in self.html.iter(include)])
        if level != 0:
            return heading + text + "\n" + "\n".join([subsection.get_text(level - 1, exclude) for subsection in self.subsections])
        else:
            return heading + text

    def get_reference_ids(self, level = 0, reference_ids = []):
        """
        Get reference ids in the section.

        Args:
            level: The depth to which reference ids from subsections will be retrieved.
        Returns:
            A list of reference ids as strings.
        """
        reference_ids += [element.get("id") for element in self.html.iter() if element.get("class") == "reference"]
        if level != 0:
            for subsection in self.subsections:
                subsection.get_reference_ids(level - 1, reference_ids)
        return reference_ids

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

    def tree(self):
        """
        Creates a nested section tree from this section.

        Returns:
            A section tree of headings, paragraphs and divs.
        """
        html = deepcopy(self.html)
        self.html.clear()
        for element in html:
            if element.tag not in self.headings[:1]:
                if not self.subsections:
                    self.html.append(element)
                else:
                    self.subsections[-1].append(element)
            else:
                self.subsections.append(HTML.fromstring('<div> class="section" </div>'))
                self.subsections[-1].append(element)
        self.subsections = [self._html_to_section(html) for html in self.subsections]
        self._siblings()
        return self

    def _html_to_section(self, html):
        """
        Turns a list of elements into a new subsection and calls tree on it.

        Args:
            elements: A list of HTML elements.
            name: The name of the subsection.
            level: The level of this subsection.
        """
        if html is not None:
            name = html[0].xpath("string()")
            subsection = Section(html, name, self, self.level + 1, self.headings[1:])
            subsection.tree()
            return subsection

    def _siblings(self):
        for subsection1,subsection2 in zip(self.subsections[:-1], self.subsections[1:]):
            subsection1.next = subsection2
            subsection2.prev = subsection1
        for subsection in self.subsections:
            subsection._siblings()

    def find(self, strings, sections = []):
        """
        Recursively finds all subsections in the section tree with any of the given strings in the title.

        Args:
            string: A list of strings to search in the title.
            sections: Sections that will be returned.
        Returns:
            A list of sections.
        """
        for subsection in self.subsections:
            for string in strings:
                if string in subsection.name:
                    sections.append(subsection)
                    break
            subsection.find(strings, sections)
        return sections

    def get_paragraphs(self, paragraphs = []):
        paragraphs += [element for element in self.html.iter(["p"])]
        for subsection in self.subsections:
            subsection.get_paragraphs(paragraphs)
        return paragraphs

    def get_headings(self, headings = []):
        headings += [element for element in self.html.iter(["h2","h3","h4","h5","h6"])]
        for subsection in self.subsections:
            subsection.get_headings(headings)
        return headings

    def get_lists(self, lists = []):
        lists += [element for element in self.html.iter(["ol","ul"])]
        for subsection in self.subsections:
            subsection.get_lists(lists)
        return lists

    def get_tables(self, tables = []):
        tables += [element for element in self.html.iter(["table"])]
        for subsection in self.subsections:
            subsection.get_tables(tables)
        return tables

    def get_captions(self, captions = []):
        captions += [element for element in self.html.iter() if element.get("class") == "thumbcaption"]
        for subsection in self.subsections:
            subsection.get_captions(captions)
        return captions

    def parent_path(self):
        """
        Get the path of parent names.

        Returns:
            The pipe-separated path to this section.
        """
        if not self.parent:
            return "root"
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
