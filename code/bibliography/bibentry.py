from requests import get
from time import sleep
from random import randint, random

class Bibentry:
    """
    Wrapper class for bibentry.

    Attributes:
        bibkey: The bibkey of this bibentry.
        title: The title of this bibentry.
        authors: The authors of this bibentry.
        doi: The doi of this bibentry.
        pmid: The pmid of this bibentry.
        year: The year of this bibentry.
    """
    def __init__(self, bibkey, bibentry):

        self.bibkey = bibkey
        self.title = bibentry.get("title", None)
        self.authors = [author[0] for author in bibentry.get("authors")]
        self.doi = bibentry.get("doi", None)
        self.pmid = bibentry.get("pmid", None)
        self.year = bibentry.get("year", None)

    def doi_valid(self):
        """
        Validates DOI using doi.org.
        """
        header = {'user-agent': 'Modzilla/5.0 (X11; Ubuntu; Linux x86_64; rv:81.0) Gecko/20100101 Firefox/81.0'}
        sleep(self._delay())
        return get("https://doi.org/" + self.doi, headers = header, timeout = 5).status_code != 404

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.bibkey == other.bibkey

    def __ne__(self, other):
        return not self == other

    def _delay(self):
        """
        Request delay between 2 and 4 seconds.
        
        Returns:
            Float between 2 and 4.
        """
        return 2 + randint(0,1) + random()
