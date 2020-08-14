from bibliography.author import Author
from pprint import pformat

class Bibentry:
    """
    Wrapper class for bibentry in bibliography CSV.

    Attributes:
        wos: Wos extracted from bibentry.
        title = Title extracted from bibentry.
        author = Wrapped author object as extracted from bibentry.
        source = Source extracted from bibentry.
        page_start = First page extracted from bibentry.
        page_end = Last page extracted from bibentry.
        volume = Volume extracted from bibentry.
        year = Year extracted from bibentry.
        doi = Doi extracted from bibentry.
    """
    def __init__(self, data):
        """
        Initialises the bibentry.

        Args:
            row: A row as extracted from the bibliography csv.
        """
        self.wos = data["wos"].lower()
        self.title = data["title"].lower()
        self.author = Author(data["author"])
        self.source = data["source"].lower()
        self.page_start = data["pages"].split("-")[0]
        self.page_end = data["pages"].split("-")[-1]
        self.issue = data["issue"]
        self.volume = data["volume"]
        self.year = int(data["year"])
        self.doi = data["doi"].lower()

    def __str__(self):
        string_representation = self.__dict__.copy()
        string_representation["author"] = self.author.__dict__
        return pformat(string_representation)

    def bibtex(self):
        dictionary_representation = self.__dict__.copy()
        dictionary_representation["author"] = self.author.fullname
        dictionary_representation["pages"] = self.page_start + "--" + self.page_end
        del dictionary_representation["page_start"]
        del dictionary_representation["page_end"]
        dictionary_representation["year"] = str(dictionary_representation["year"])
        dictionary_representation["ENTRYTYPE"] = "article"
        dictionary_representation["ID"] = self.author.surname.lower() + ":" + str(self.year)
        return dictionary_representation

