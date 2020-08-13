from bibliography.bibentry import Bibentry
from os.path import exists, basename, dirname, sep
from os import makedirs
from csv import reader
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
            filepath: The path to the bibliohgraphy CSV.
        """
        self.filepath = filepath
        self.bibentries = []
        with open(filepath) as file:
            csv_reader = reader(file, delimiter="\t")
            for row in csv_reader:
                self.bibentries.append(Bibentry(row))
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
        if filepath:
            if not exists(dirname(filepath)): makedirs(dirname(filepath))
        else:
            filepath = dirname(self.filepath) + sep + basename(self.filepath).split(".")[0] + "." + "bib"
        with open(filepath, "w") as file:
            for bibentry in self.bibentries:
                file.write(bibentry.to_bibtex())

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
