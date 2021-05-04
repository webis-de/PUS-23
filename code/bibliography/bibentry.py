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
        journal: The journal of this bibentry.
        doi: The doi of this bibentry.
        pmid: The pmid of this bibentry.
        year: The year of this bibentry.
    """
    def __init__(self, bibentry):

        self.bibkey = bibentry.key
        self.title = self.replace_braces(bibentry.fields.get("title", None))
        self.authors = [self.replace_braces(person.last_names[0]) for person in bibentry.persons.get("author") if self.replace_braces(person.last_names[0])]
        self.journal = bibentry.fields.get("journal", None)
        self.doi = bibentry.fields.get("doi", None)
        self.pmid = bibentry.fields.get("pmid", None)
        self.year = bibentry.fields.get("year", None)

    def replace_braces(self, value):
        """
        Replaces curly braces in a string or the string elements of a list or tuple.

        Returns:
            The string or list or tuple provided, with curly braces removed.
        """
        if type(value) == str:
            return value.replace("{","").replace("}","")
        elif type(value) == list:
            return [string.replace("{","").replace("}","") for string in value]
        elif type(value) == tuple:
            return tuple(string.replace("{","").replace("}","") for string in value)
        else:
            ""

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
