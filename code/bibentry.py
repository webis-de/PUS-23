from pprint import pformat
from author import Author

class Bibentry:
    """
    Wrapper class for author.

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
        self.volume = row[7]
        self.year = int(row[8])
        self.doi = row[9].lower()

    def __str__(self):
        string_representation = self.__dict__
        string_representation["author"] = self.author.__dict__
        return pformat(string_representation)

if __name__ == "__main__":
    
        bibentry = Bibentry("WOS:000227707100005	CRISPR ELEMENTS IN YERSINIA PESTIS ACQUIRE NEW REPEATS BY PREFERENTIAL UPTAKE OF BACTERIOPHAGE DNA, AND PROVIDE ADDITIONAL TOOLS FOR EVOLUTIONARY STUDIES	POURCEL,C	MICROBIOLOGY-SGM	653	663		151	2005	10.1099/MIC.0.27437-0".split("\t"))
        print(bibentry)
