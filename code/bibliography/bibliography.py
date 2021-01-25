from .bibentry import Bibentry
from os.path import exists, sep
from os import makedirs
from pybtex.database import parse_file
import matplotlib.pyplot as plt

class Bibliography:
    """
    Wrapper class for bibliography.

    Attributes:
        filepath: Path to BIB file.
        bibentries: A list of Bibentry objects deserialised from BIB file.
        titles: A list of all titles in the bibliography (lowered).
        authors: A list of all authors in the bibliography (first author, surname).
        dois: A list of all dois in the bibliography (lowered).
        years: A list of all years in the bibliography.
    """
    def __init__(self, filepath):
        """
        Intitialises the bibliography from the file provided using Pybtex.

        Args:
            filepath: The path to the bibliohgraphy file.
        """
        self.filepath = filepath
        self.bibentries = {bibkey:Bibentry(bibentry) for bibkey,bibentry in parse_file(filepath).entries.items()}
        self.titles = [bibentry.title for bibentry in self.bibentries.values()]
        self.authors = sorted(set([bibentry.authors[0] for bibentry in self.bibentries.values()]))
        self.dois = [bibentry.doi for bibentry in self.bibentries.values()]
        self.years = [int(bibentry.year) for bibentry in self.bibentries.values()]        

    def field_values(self, field):
        """
        Get field values for all entries.

        Args:
            field: The field for which values are required.

        Returns:
            List of values behind the field of each entry in the Bibliography.
        """
        if field == "titles":
            return self.titles
        if field == "authors":
            return self.authors
        if field == "dois":
            return self.dois
        if field == "years":
            return self.years

    def get_bibentries(self, bib_keys):
        """
        Get all Bibentries pertaining to the bib_keys provided.

        Args:
            bib_keys: A list of String representing bib_keys.
        Returns:
            A list of Bibentries.
        """
        bibentries = []
        for bib_key in bib_keys:
            publication = self.bibentries.get(bib_key)
            if publication:
                bibentries.append(publication)
        return bibentries

    def plot_publication_distribution_to_file(self, directory):
        """
        Plot the distribution of publications across the entire bibliography to file.
        Revisions are accumulated per year.

        Args:
            directory: The directory to save the plot to.
        """
        distribution = {year:self.years.count(year) for year in set(sorted(self.years))}

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
