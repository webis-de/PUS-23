from re import sub
from lxml import etree
from queue import Queue

class Section:

    def __init__(self, source, name = "root", parent = None, level = 0, headings = ["h2","h3","h4","h5","h6"]):

        self.source = source
        self.name = name
        self.parent = parent
        self.prev = None
        self.next = None
        self.level = level
        self.subsections = []
        self.headings = headings

    def get_text(self, deep = True):
        """
        Get the full text of the element.

        Args:
            deep: Get text below top level.
        Returns:
            The full section as a string.
        """
        return sub(r" +", " ", " ".join(self.source.xpath("./" + ("/" * deep) + "text()")))

    def get_hrefs(self, deep = True):
        """
        Return all hrefs in the element.

        Args:
            deep: Get hrefs below top level.
        Returns:
            A list of hrefs as strings.
        """
        return [element.get("href") for element in self.source.xpath("./" + ("/" * deep) + "a")]

    def tree(self, level = 1):
        """
        Creates a nested section tree from this section.

        Args:
            level: Level of this section in the tree; 'root' at 0.
        Returns:
            A section tree of headings, paragraphs and divs.
        """
        if any([element.tag not in  ["p","div"] for element in self.source]):
            elements = []
            name = "Intro"
            for element in self.source:
                if element.tag in ["p","div"] + self.headings[1:]:
                    elements.append(element)
                elif element.tag in self.headings[:1]:
                    self._elements_to_subsection(elements, name, level)
                    name = "".join(element.itertext())
                    elements = []
            self._elements_to_subsection(elements, name, level)
        else:
            self.subsections = [Section(element, element.tag, self, level) for element in self.source]
        return self._siblings()

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

    def _elements_to_subsection(self, elements, name, level):
        """
        Turns a list of elements into a new subsection and calls tree on it.

        Args:
            elements: A list of HTML elements.
            name: The name of the subsection.
            level: The level of this subsection.
        """
        if elements:
            subsection = Section(elements, name, self, level, self.headings[1:])
            self.subsections.append(subsection)
            subsection.tree(level + 1)

    def _siblings(self):
        for subsection1,subsection2 in zip(self.subsections[:-1], self.subsections[1:]):
            subsection1.next = subsection2
            subsection2.prev = subsection1
        for subsection in self.subsections:
            subsection._siblings()
        return self

    def _queue_subsections(self):
        """
        Helper function to queue subsections breadth-first.

        Returns:
            A Queue of subsections, breadth-first.
        """
        queue = Queue()
        for subsection in self.subsections:
            queue.put(subsection)
        for subsection in self.subsections:
            for subsubsection in subsection.subsections:
                queue.put(subsubsection)
        return queue

    def parent_path(self):
        """
        Get the path of parent names.

        Returns:
            The /-separated path to this section.
        """
        if not self.parent:
            return ""
        else:
            return self.parent.parent_path() + "/" + self.name

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
        
        if self.subsections:
            json = {"level":self.level,
                    "parent":self.parent_name(),
                    "path":self.parent_path(),
                    "prev":self.prev.name if self.prev else None,
                    "next":self.next.name if self.next else None}
            json[self.name] = {index:element.json() for index,element in enumerate(self.subsections,1)}
        else:
            json = {}
            json = {"level":self.level,
                    "parent":self.parent_name(),
                    "path":self.parent_path(),
                    "prev":"".join(self.prev.source.itertext()).replace("\n","").strip() if self.prev else None,
                    "next":"".join(self.next.source.itertext()).replace("\n","").strip() if self.next else None,
                    self.name:"".join(self.source.itertext()).replace("\n","").strip()}
        return json

