from re import findall, finditer, search, split, sub, S

class Source:
    """
    Wrapper class for Wikipedia sources such as 'References' and 'Further Reading'.

    Attributes:
        source: The source of the reference as HTML/XML.
    """

    def __init__(self, html):
        """
        Initialise the reference using its source code and running index.
        
        source: The html of the reference.
        """
        self.html = html

    def get_text(self):
        """
        Get the full text of the reference.

        Returns:
            The full reference as a string.
        """
        reference_text = self.html.find(".//cite")
        if reference_text is not None:
            return reference_text.xpath("string()")
        else:
            return self.html.xpath("string()")

    def get_reference_ids(self):
        """
        Get HTML id of source.

        Returns:
            A string id.
        """
        return [sub("^#cite","cite", element.get("href")) for element in self.html.iter("a")]

    def get_superscript(self, revision): # unreliable!
        """
        Get the superscript that points to the footnore holding the reference.
        Returns:
            A superscript in square brackets as string, e.g. '[16]'
        """
        try:
            return [i.xpath(".//text()")[0].strip() for i in revision.etree_from_html().xpath(".//sup[@class='reference']/a[@href='#{}']".format(self.get_id()))][0]
        except IndexError:
            return ""

    def get_number_via_id(self): # unreliable!
        """
        Get the 1-indexed number of the source.
        """
        try:
            return self.get_id().split("-")[-1]
        except IndexError:
            return ""

    def linked_sections(self, sections):
        linked_sections = set()
        source_id = "#" + self.get_id()
        for section in sections:
            if source_id in section.get_hrefs():
                linked_sections.add(section)
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
                #try to find quoted title
                matches = list(finditer(r"\".*?\"", text))
                #get longest match
                match = sorted(matches, key=lambda match: match.end() - match.start(), reverse=True)[0]
                #get span of match
                text = text[match.start():match.end()]
                #remove quotation marks
                title = text.replace("\"", "")
            except IndexError:
                try:
                    #split at year
                    text = split(r"\(.*?\)\.? ?", text, 1)[1].strip()
                    #split at stop and get first element
                    text = text.split(".")[0]
                    #remove quotation marks
                    title = text.replace("\"", "")
                except IndexError:
                    return ""
            return title
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
        for element in self.html.xpath(".//a[contains(@href, 'doi.org/')]"):
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
        for element in self.html.xpath(".//a[contains(@href, 'pubmed')]"):
            pmid = search("\d+", element.get("href").split("/")[-1])
            if pmid:
                PMIDs.add(pmid.group(0))
        #pmifs in text
        for pmid in findall("pmid.*?\d+", self.get_text().lower()):
            pmid = search("\d+", pmid)
            if pmid:
                PMIDs.add(pmid.group(0))
        return [pmid for pmid in PMIDs if pmid]

    def get_pmcs(self):
        """
        Get all unique PUBMED IDs.

        Returns:
            A list of PMCs as strings.
        """
        PMCs = set()
        #pmids from hrefs
        for element in self.html.xpath(".//a[contains(@href, 'pmc/')]"):
            pmc = search("\d+", element.get("href").split("/")[-1])
            if pmc:
                PMCs.add(pmc.group(0))
        #pmifs in text
        for pmc in findall("pmc.*?\d+", self.get_text().lower()):
            pmc = search("\d+", pmc)
            if pmc:
                PMCs.add(pmc.group(0))
        return [pmc for pmc in PMCs if pmc]

    def get_identifiers(self):
        """
        Get all idendentifiers (DOI, PMC, PMID)

        Returns:
            A dictionary of found identifiers (values as strings) 
            Emty if nothing found.
        """
        return {
            'DOI': self.get_dois()[0] if self.get_dois() else '',
            'PMID': self.get_pmids()[0] if self.get_pmids() else '',
            'PMC': self.get_pmcs()[0] if self.get_pmcs() else '',
        }

    
