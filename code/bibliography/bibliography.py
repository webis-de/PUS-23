from .bibentry import Bibentry
from os.path import exists, sep
from os import makedirs
from csv import reader
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
        self.bibentries = {}
        i = 1
        with open(filepath) as file:
            csv_reader = reader(file, delimiter="|")
            header = next(csv_reader)
            columns = {column:header.index(column) for column in header}
            for row in csv_reader:
                i += 1
                try:
                    self.bibentries[row[0]] = Bibentry(row[0],
                                                       {"title":row[columns["title"]],
                                                        "authors":[author.split(",") for author in row[columns["authors"]].split("|")],
                                                        "doi":row[columns["doi"]],
                                                        "pmid":row[columns["pmid"]],
                                                        "year":row[columns["year"]]})
                except:
                    input(i)
        self.titles = [bibentry.title for bibentry in self.bibentries.values()]
        self.authors = sorted(set([bibentry.authors[0] for bibentry in self.bibentries.values()]))
        self.dois = [bibentry.doi for bibentry in self.bibentries.values()]
        self.pmids = [bibentry.pmid for bibentry in self.bibentries.values()]
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
            bib_keys: A list of strings representing bib_keys.
        Returns:
            A dictionary of Bibentries.
        """
        bibentries = {}
        for bib_key in bib_keys:
            if bib_key in self.bibentries:
                bibentries[bib_key] = self.bibentries[bib_key]
            else:
                print("Missing bibkey:", bib_key)
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

if __name__ == "__main__":

    def replace_braces(value):
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

    from csv import writer, reader
    from pybtex.database import parse_file as pybtex_parse_file
    bib = pybtex_parse_file("../../data/CRISPR_literature.bib").entries.values()
    with open("CRISPR_literature_from_bib.csv", "w") as file:
        csv_writer = writer(file, delimiter=",")
        csv_writer.writerow(["unique-id","title","authors","doi","pmid","eissn","issn","year","month","journal","number","volume","pages"])
        for bibentry in bib:
            csv_writer.writerow([bibentry.fields.get("unique-id", "").replace("ISI","WOS"),
                                 replace_braces(bibentry.fields.get("title", "")),
                                 "|".join([replace_braces(person.last_names[0]) + "," + replace_braces(person.first_names[0]) for person in bibentry.persons.get("author", "")]),
                                 bibentry.fields.get("doi", ""),
                                 bibentry.fields.get("pmid", ""),
                                 bibentry.fields.get("eissn", ""),
                                 bibentry.fields.get("issn", ""),
                                 bibentry.fields.get("year", ""),
                                 bibentry.fields.get("month", ""),
                                 bibentry.fields.get("journal", ""),
                                 bibentry.fields.get("number", ""),
                                 bibentry.fields.get("volume", ""),
                                 bibentry.fields.get("pages", "")])
        
    b = Bibliography("CRISPR_literature_from_bib.csv")
    for key,value in b.bibentries["WOS:000282599700029"].__dict__.items():
        print(key, value)
