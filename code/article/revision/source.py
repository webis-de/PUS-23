from re import findall, finditer, search, split, sub, S

class Source:
    """
    Wrapper class for Wikipedia sources such as 'References' and 'Further Reading'.

    Attributes:
        source: The source of the reference as HTML/XML.
    """

    def __init__(self, source):
        """
        Initialise the reference using its source code and running index.
        
        source: The source of the reference as HTML/XML.
        """
        self.source = source

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

    def get_id(self):
        """
        Get HTML id of source.

        Returns:
            A string id.
        """
        return self.source.get("id", "")

    def get_number(self):
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

    def get_pmcs(self):
        """
        Get all unique PUBMED IDs.

        Returns:
            A list of PMCs as strings.
        """
        PMCs = set()
        #pmids from hrefs
        for element in self.source.xpath(".//a[contains(@href, 'pmc/')]"):
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
        Comment:
            Arno-style search and parsing without regex and in one dict comprehension (may be faster)
        """
        nofollows = self.source.xpath(".//a[@rel='nofollow']")
        return {'DOI' if 'doi.org' in tag.get('href') 
            else 'PMC' if 'pmc' in tag.get('href') 
            else 'PMID':
                         tag.get('href').split('/')[-1] if 'doi.org' in tag.get('href')
                    else tag.get('href').split('/')[-1].split('PMC')[-1] if 'pmc' in tag.get('href')
                    else tag.get('href').split('/')[-1].split('?')[0] # = 'pubmed'
            for tag in nofollows 
            if any(i in tag.get('href') for i in ['doi.org','pmc','pubmed'])} 
