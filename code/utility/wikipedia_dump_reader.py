import bz2
##from lxml.etree import ElementTree as LXMLET
##from xml.etree import ElementTree as XMLET
from re import findall, sub

class WikipediaDumpReader(object):

    def __init__(self, filepath, article_titles = []):
        self.filepath = filepath
        self.bz2_file = bz2.open(self.filepath, "rb")
        self.namespaces = {"":"http://www.mediawiki.org/xml/export-0.10/"}
        self.article_titles = set(article_titles)

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

##    def xml_iter(self):
##        read_revisions = False
##        read_pageid = False
##        xml = XMLET.iterparse(self.bz2_file)
##        for event, element in xml:
##            if element.tag.split("}")[-1] == "title":
##                title = element.text
##            elif element.tag.split("}")[-1] == "ns":
##                read_revisions = element.text == "0"
##                read_pageid = True
##            elif element.tag.split("}")[-1] == "id" and read_pageid:
##                pageid = element.text
##            elif read_revisions:
##                if element.tag.split("}")[-1] == "revision":
##                    read_pageid = False
##                    for subelement in element:
##                        if subelement.tag.split("}")[-1] == "id":
##                            revid = subelement.text
##                        if subelement.tag.split("}")[-1] == "timestamp":
##                            timestamp = subelement.text
##                        if subelement.tag.split("}")[-1] == "text":
##                            text = subelement.text
##                    yield (title,pageid,revid,timestamp,text)
##                    element.clear()
##            else:
##                element.clear()

    def lxml_iter(self):
        xml = LXMLET().parse(self.bz2_file)
        for page in xml.findall("page", self.namespaces):
            if page.find("ns", self.namespaces).text == "0":
                title = page.find("title", self.namespaces).text
                if self.article_titles and title not in self.article_titles:
                    continue
                pageid = page.find("id", self.namespaces).text
                for revision in page.findall("revision", self.namespaces):
                    yield (title,
                           pageid,
                           revision.find("id", self.namespaces).text,
                           revision.find("timestamp", self.namespaces).text,
                           revision.find("text", self.namespaces).text)

    def line_iter(self):
        with bz2.open(self.filepath, "rt") as bz2_file:
            read_revisions = False
            read_text = False
            title = None
            text = ""

            for line in bz2_file:
                if read_text:
                    if line.startswith("      <sha1"):
                        text = sub("</text>","",text)
                        yield (title,
                               pageid,
                               revid,
                               timestamp,
                               text)
                        read_text = False
                        text = ""
                    else:
                        text += line
                else:
                    if line.startswith("    <title"):
                        title = line[11:-9]
                    elif line.startswith("    <id"):
                        pageid = line[8:-6]
                    elif title and self.article_titles and title not in self.article_titles:
                        continue
                    elif line.startswith("    <ns"):
                        read_revisions = (line[8] == "0")
                    elif read_revisions:
                        if line.startswith("      <id"):
                            revid = line[10:-6]
                        elif line.startswith("      <timestamp"):
                            timestamp = line[17:-13]
                        elif read_revisions and line.startswith("      <text"):
                            text += sub("      <text.*?>","",line)
                            read_text = True
