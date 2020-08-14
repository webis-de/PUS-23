from bibliography.bibentry import Bibentry
from os.path import exists, basename, dirname, sep
from os import makedirs
from csv import reader
from bibtexparser import load
from bibtexparser.bparser import BibTexParser
from bibtexparser.customization import homogenize_latex_encoding
from bibtexparser.bwriter import BibTexWriter
from bibtexparser.bibdatabase import BibDatabase
import matplotlib.pyplot as plt

class Bibliography:
    """
    Wrapper class for bibliography CSV.

    Attributes:
        filepath: Path to the CSV file.
        bibentries: A list of Bibentry objects deserialised from CSV rows.
        titles: A list of all titles in the bibliography.
        authors: A list of all authors in the bibliography.
        dois: A list of all dois in the bibliography.
        years: A list of all years in the bibliography.
    """
    def __init__(self, filepath):
        """
        Intitialises the bibliography from the file provided.

        Args:
            filepath: The path to the bibliohgraphy file.
        """
        self.filepath = filepath
        self.bibentries = []

    def from_csv(self):
        columns = ["wos","title","author","source","page_start","page_end","issue","volume","year","doi"]
        with open(self.filepath) as csv_file:
            csv_reader = reader(csv_file, delimiter="\t")
            for row in csv_reader:
                data = {columns[i]:row[i] for i in range(len(row))}
                data["pages"] = data["page_start"] + "-" + data["page_end"]
                del data["page_start"]
                del data["page_end"]
                self.bibentries.append(Bibentry(data))
            self.bibentries = sorted(self.bibentries, key = lambda bibentry: bibentry.author.surname)
        self.load_bibkey_values()
        return self

    def from_bib(self):
        with open(self.filepath) as bib_file:
            parser = BibTexParser()
            parser.customization = homogenize_latex_encoding
            bib_database = load(bib_file, parser=parser)
            self.bibentries = [Bibentry([entry["wos"],
                                        entry["title"],
                                        entry["author"],
                                        entry["source"],
                                        entry["pages"].split("-")[0],
                                        entry["pages"].split("-")[1],
                                        entry["issue"],
                                        entry["volume"],
                                        entry["year"],
                                        entry["doi"]]) for entry in bib_database.get_entry_dict().values()]
        self.load_bibkey_values()
        return self

    def load_bibkey_values(self):
        self.titles = [bibentry.title.lower() for bibentry in self.bibentries]
        self.authors = [bibentry.author.surname for bibentry in self.bibentries]
        self.dois = [bibentry.doi.lower() for bibentry in self.bibentries]
        self.years = [bibentry.year for bibentry in self.bibentries]        

    def bibkey_values(self, bibkey):
        """
        Getter for bibkey values.

        Args:
            bibkey: The bibkey for which values are required.

        Returns:
            List of values behind each bibkey in the Bibliography.
        """
        if bibkey == "titles":
            return self.titles
        if bibkey == "authors":
            return self.authors
        if bibkey == "dois":
            return self.dois
        if bibkey == "years":
            return self.years

    def write_bibtex_file(self, filepath = None):
        """
        Convert bibentries to BibText and write to file.

        Args:
            filepath: The path to the file to which the bibvalues will be written.
                      Defaults to directory and name of source file of Bibliography.
        """
        db = BibDatabase()
        db.entries = [bibentry.bibtex() for bibentry in self.bibentries]

        if filepath:
            if not exists(dirname(filepath)): makedirs(dirname(filepath))
        else:
            filepath = dirname(self.filepath) + sep + basename(self.filepath).split(".")[0] + "." + "bib"
        with open(filepath, "w") as bibfile:
            writer = BibTexWriter()
            bibfile.write(writer.write(db))    

    def plot_publication_distribution_to_file(self, directory):
        """
        Plot the distribution of publications across the entire bibliography to file.
        Revisions are accumulated per year.

        Args:
            directory: The directory to save the plot to.
        """
        distribution = {year:0 for year in range(min(self.years),max(self.years) + 1)}
        for bibentry in self.bibentries:
            distribution[int(bibentry.year)] += 1

        plt.figure(figsize=(25,10), dpi=150)
        plt.title("Publication Distribition")
        plt.margins(x=0.01,y=0.1)
        plt.xlabel('year')
        plt.ylabel('number of publications')
        plt.bar(list(range(len(distribution))), list(distribution.values()))
        plt.xticks(list(range(len(distribution))), list(distribution.keys()), rotation='vertical')
        plt.subplots_adjust(bottom=0.1, top=0.95, left=0.03, right=0.995)
        if not exists(directory): makedirs(directory)
        plt.savefig(directory + sep + "publication_distribution.png")
