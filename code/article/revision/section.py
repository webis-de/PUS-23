from re import sub
from lxml import etree
from queue import Queue

class Section:

    def __init__(self, source, name = "", parent = None, headings = ["h2","h3","h4","h5","h6"]):

        self.source = source
        self.name = name
        self.parent = parent
        self.subsections = []
        self.headings = headings

    def get_text(self, deep = True):
        """
        Get the full text of the element.

        Returns:
            The full section as a string.
        """
        return sub(r" +", " ", " ".join(self.source.xpath("./" + ("/" * deep) + "text()")))

    def get_hrefs(self, deep = True):
        """
        Return all hrefs in the element.

        Returns:
            A list of hrefs as strings.
        """
        return [element.get("href") for element in self.source.xpath("./" + ("/" * deep) + "a")]

    def tree(self):
        if any([element.tag not in  ["p","div"] for element in self.source]):
            elements = []
            name = "Intro"
            for element in self.source:
                if element.tag in ["p","div"] + self.headings[1:]:
                    elements.append(element)
                elif element.tag in self.headings[:1]:
                    if elements:
                        self.subsections.append(Section(elements, name, self, self.headings[1:]))
                        self.subsections[-1].tree()
                    name = element.xpath(".//text()")[0]
                    elements = []
            if elements:
                self.subsections.append(Section(elements, name, self, self.headings[1:]))
                self.subsections[-1].tree()
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

    def nested_json(self, first=True):
        """
        Return this section as a json object.

        Returns:
            This section as a dictionary.
        """
        json = {}
        #if not first: json["text"] = self.get_text(deep=True).replace("\n","")
        if self.subsections:
            json[self.name] = [element.nested_json(False) for element in self.subsections]
        else:
            json[self.name] = {index:"".join(element.itertext()).replace("\n","").strip() for index,element in enumerate(self.source,1)}
        return json

