from re import findall, finditer, search, split, sub, S

class Reference:

    def __init__(self, source, number):

        self.source = source
        self.number = number

    def text(self):
        try:
            return "".join(self.source.xpath(".//cite")[0].itertext())
        except IndexError:
            return  "".join(self.source.itertext())

    def backlinks(self):
        return [backlink.get("href")[1:] for backlink in self.source.xpath(".//span[@class='mw-cite-backlink']//a")]

    def linked_sections(self, paragraphs):
        linked_paragraphs = set()
        for paragraph in paragraphs:
            backlinks = self.backlinks()
            if backlinks and paragraph.source.xpath("|".join([".//sup[@id='" + backlink + "']" for backlink in backlinks])):
                linked_paragraphs.add(paragraph)
        return linked_paragraphs

    def get_authors(self, language):
        #get full text of reference
        text = self.text()
        AUTHORS = []
        if language == "en":
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
        if language == "de":
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
        return AUTHORS

    def get_title(self, language):
        #get full text of reference
        text = self.text()
        if language == "en":
            try:
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
                return title
            except IndexError:
                return ""
        if language == "de":
            try:
                #split at :
                text = split(":", text, 1)[1].strip()
                #split at .
                title = text.split(".")[0].strip()
                return title
            except IndexError:
                return ""

    def get_dois(self):
        DOIs = set()
        for element in self.source.xpath(".//a[contains(@href, 'doi.org/')]"):
            #dois from links
            DOIs.add(element.get("href").split("doi.org/")[-1].replace("%2F","/"))
            #dois from element text
            DOIs.add(element.text)
        return [doi for doi in DOIs if " " not in doi]

    def get_pmids(self):
        PMIDs = set()
        for pmid in findall("pmid.*?\d+", self.text().lower()):
            pmid = search("\d+", pmid)
            if pmid:
                PMIDs.add(pmid.group(0))
        return [pmid for pmid in PMIDs if pmid]
