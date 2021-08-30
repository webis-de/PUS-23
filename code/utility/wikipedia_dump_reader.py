import bz2
from xml.etree import ElementTree
from re import findall

class WikipediaDumpReader(object):

    def __init__(self, filepath):
        self.filepath = filepath
        self.bz2_file = bz2.open(self.filepath, "rb")
        self.xml_iterator = ElementTree.iterparse(self.bz2_file)
        self.namespaces = self._get_namespaces()

    def __enter__(self):
        """Makes the API autoclosable."""
        return self

    def __exit__(self, type, value, traceback):
        """Close XML file handle."""
        self.bz2_file.close()

    def _get_namespaces(self):
        namespaces = findall(r'\{.+?\}', next(self.xml_iterator)[1].tag)
        return {"":"http://www.mediawiki.org/xml/export-0.10/",
                "ns0":"http://www.mediawiki.org/xml/export-0.10/",
                "xsi":"http://www.w3.org/2001/XMLSchema-instance"}

    def __iter__(self):
        read_revisions = False
        for event, element in self.xml_iterator:
            if element.tag.split("}")[-1] == "title":
                revision = {"title":element.text} 
            elif element.tag.split("}")[-1] == "ns":
                read_revisions = element.text == "0"
            elif element.tag.split("}")[-1] == "revision" and read_revisions:
                for subelement in element:
                    if subelement.tag.split("}")[-1] == "id":
                        revision["revid"] = subelement.text
                    if subelement.tag.split("}")[-1] == "timestamp":
                        revision["timestamp"] = subelement.text
                    if subelement.tag.split("}")[-1] == "text":
                        revision["text"] = subelement.text
                yield revision
                element.clear()
            else:
                if not read_revisions: element.clear()
