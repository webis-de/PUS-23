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
    def __init__(self, row):
        """
        Initialises the bibentry.

        Args:
            row: A row as extracted from the bibliography csv.
        """
        self.wos = row[0].lower()
        self.title = row[1].lower()
        self.author = Author(row[2])
        self.source = row[3].lower()
        self.page_start = row[4]
        self.page_end = row[5]
        self.issue = row[6]
        self.volume = row[7]
        self.year = int(row[8])
        self.doi = row[9].lower()

    def __str__(self):
        string_representation = self.__dict__.copy()
        string_representation["author"] = self.author.__dict__
        return pformat(string_representation)

    def to_bibtex(self):
        string = ""
        string += "@article{" + self.author.surname.lower() + ":" + str(self.year) + "," + "\n"
        dictionary_representation = self.__dict__.copy()
        dictionary_representation["author"] = self.author.surname + ", " + self.author.firstname
        dictionary_representation["pages"] = self.page_start + "-" + self.page_end
        del dictionary_representation["page_start"]
        del dictionary_representation["page_end"]
        l = max([len(key) for key in dictionary_representation.keys()])
        for item in dictionary_representation.items():
            string += "\t" + item[0].ljust(l, " ") + " = " + "{" + str(item[1]) + "}" + "," + "\n"
        string = string[:-2] + "\n" + "}" + "\n"
        return string

