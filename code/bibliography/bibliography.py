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
        self.bibentries = parse_file(filepath).entries
        self.titles = [self.replace_braces(value) for value in [bibentry.fields.get("title") for bibentry in self.bibentries.values()]]
        self.authors = sorted(list(set([self.replace_braces(value)[0] for value in [tuple(bibentry.persons.get("author")[0].last_names + bibentry.persons.get("author")[0].first_names) for bibentry in self.bibentries.values()]])))
        self.dois = [bibentry.fields.get("doi") for bibentry in self.bibentries.values() if bibentry.fields.get("doi")]
        self.years = [int(bibentry.fields.get("year")) for bibentry in self.bibentries.values()]        

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

    def replace_braces(self, value):
        if type(value) == str:
            return value.replace("{","").replace("}","")
        if type(value) == list:
            return [string.replace("{","").replace("}","") for string in value]
        if type(value) == tuple:
            return tuple(string.replace("{","").replace("}","") for string in value)

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

if __name__ == "__main__":

    bib = Bibliography("../../data/tracing-innovations-lit.bib")
    for author in bib.authors:
        print(author)
    print("="*50)
    for title in bib.titles:
        print(title)
    print("="*50)
    for doi in bib.dois:
        print(doi)
