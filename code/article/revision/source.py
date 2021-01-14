from re import findall, finditer, search, split, sub, S

class Source:
    """
    Wrapper class for Wikipedia sources such as 'References' and 'Further Reading'.

    Attributes:
        source: The source of the reference as HTML/XML.
        number: The running index of the reference.
    """

    def __init__(self, source, number):
        """
        Initialise the reference using its source code and running index.
        
        source: The source of the reference as HTML/XML.
        number: The running index of the reference.
        """
        self.source = source
        self.number = number

    def get_text(self):
        """
        Get the full text of the reference.

        Returns:
            The full reference as a string.
        """
        try:
            return "".join(self.source.xpath(".//cite")[0].itertext())
        except IndexError:
            return  "".join(self.source.itertext())

    def get_backlinks(self):
        """
        Return all backlinks in the reference.

        Returns:
            A list of backlinks as strings.
        """
        return [backlink.get("href")[1:] for backlink in self.source.xpath(".//span[@class='mw-cite-backlink']//a")]

    def linked_sections(self, sections):
        linked_sections = set()
        for paragraph in sections:
            backlinks = self.get_backlinks()
            if backlinks and paragraph.source.xpath("|".join([".//sup[@id='" + backlink + "']" for backlink in backlinks])):
                linked_sections.add(paragraph)
        return linked_sections

    def get_authors(self, language):
        """
        Get all authors in the reference.

        Returns:
            List of tuples (surname, firstname).
        """
        #get full text of reference
        text = self.get_text()
        AUTHORS = []
        if language == "en":
            if "(" in text:
                #remove everything after first (
                text = sub(r"\(.*", "", text)
                #remove everything after et al.
                text = sub(r",? *et al.*", "", text)
                #remove abbreviation dots
                text = text.replace(".", "")
                #strip text
                text = text.strip()
                #get surnames and fistnames
                for author in split(r"[,;] ?", text):
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
        """
        Returns the title of the reference.

        Returns:
            The title of the reference; empty string if title cannot be found.
        """
        #get full text of reference
        text = self.get_text()
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
        """
        Get all unique DOIs in the reference.

        Returns:
            A list of DOIs as strings.
        """
        DOIs = set()
        #dois from hrefs
        for element in self.source.xpath(".//a[contains(@href, 'doi.org/')]"):
            #dois from links
            DOIs.add(element.get("href").split("doi.org/")[-1].replace("%2F","/"))
            #dois from element text
            DOIs.add(element.text)
        #dois from text
        for doi in findall("10.\d{4,9}/[-\._;\(\)/:a-zA-Z0-9]+", self.get_text()):
            if doi[-1] == ".": doi = doi[:-1]
            DOIs.add(doi)
        return [doi for doi in DOIs if " " not in doi]

    def get_pmids(self):
        """
        Get all unique PUBMED IDs.

        Returns:
            A list of PMIDs as strings.
        """
        PMIDs = set()
        #pmids from hrefs
        for element in self.source.xpath(".//a[contains(@href, 'pubmed')]"):
            pmid = search("\d+", element.get("href").split("/")[-1])
            if pmid:
                PMIDs.add(pmid.group(0))
        #pmifs in text
        for pmid in findall("pmid.*?\d+", self.get_text().lower()):
            pmid = search("\d+", pmid)
            if pmid:
                PMIDs.add(pmid.group(0))
        return [pmid for pmid in PMIDs if pmid]
