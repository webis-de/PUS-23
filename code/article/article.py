from .revision.revision import Revision
from os.path import basename, exists, sep
from os import makedirs
from json import loads, dump
import matplotlib.pyplot as plt

class Article:
    """
    Reads line JSON file of revision history of Wikipedia article and
    allows tracking, saving and plotting of bibentry value and phrase occurances.

    Attributes:
        filepath: The path to the JSON file.
        filename: The name of the JSON file.
        name: The name of the article.
        revisions: The individual revisions of the article.
        timestamps: The timestamps of all revisions.
    """
    def __init__(self, filepath):
        """
        Args:
            filepath: The path to the JSON file.
        """
        self.filepath = filepath
        self.filename = basename(filepath)
        self.name = self.filename.replace(".","_")
        self.revisions = []
        self.timestamps = []

    def get_revisions(self, first = 0, final = float("inf")):
        """
        Get revisions from first to final as provided (both included).
        Will return all revisions on file if no parameters provided.

        Args:
            first: First revision index to return.
            final: Final revision to return.

        Returns:
            A list of revisions.
        """
        with open(self.filepath) as file:
            for line in enumerate(file):
                if line[0] < first:
                    continue
                if line[0] > final:
                    break
                revision = loads(line[1])
                self.revisions.append(Revision(**revision))
        self.timestamps = [revision.timestamp.string for revision in self.revisions]
        return self.revisions

    def get_revision(self, index = None, revid = None):
        """
        Gets the first revision on file with the provided index or revid.

        Args:
            index: The index of the revision.
            revid: The revid of the revision.

        Returns:
            A revision; None if index or revid does not match.
        """
        revisions = self.yield_revisions()
        revision = next(revisions)
        while revision:
            if revision.index == index:
                return revision
            if revision.revid == revid:
                return revision
            revision = next(revisions)

    def yield_revisions(self):
        """
        Provides an iterartor over all revisions on file.

        Yields:
            A revision.
        """
        with open(self.filepath) as file:
            for line in file:
                revision = loads(line)
                yield Revision(**revision)

    def bibliography_analysis(self):
        """
        Checks the revision history of an article for titles, DOIs and PMIDs
        and writes them to a JSON file in the same directory.

        Titles with no more than 80 percent alphabetical characters (whitespace excluded)
        are discarded. Titles are not cleaned for near-duplicates.
        """
        revisions = self.yield_revisions()

        revision = next(revisions, None)

        bib = {"titles":{}, "dois":{}, "pmids":{}}

        while revision:
            print(revision.index)
            for source in revision.get_references() + revision.get_further_reading():
                title = source.get_title(self.filename.split("_")[-1])
                if title:
                    if title not in bib["titles"]:
                        if len([c for c in title.replace(" ","") if c.isalpha()])/len(title) > 0.8:
                            bib["titles"][title] = source.get_text()
                doi_set = source.get_dois()
                for doi in doi_set:
                    if doi not in bib["dois"]:
                        bib["dois"][doi] = source.get_text()
                pmid_set = source.get_pmids()
                for pmid in pmid_set:
                    if pmid not in bib["pmids"]:
                        bib["pmids"][pmid] = source.get_text()
            revision = next(revisions, None)

        with open(self.filepath + "_bib.json", "w") as file:
            dump(bib, file)

    def track_field_values_in_article(self, fields, bibliography):
        """
        Generates tracks of all field values of all bibentries in bibliography provided.

        Args:
            fields: A list of fields.
            bibliography: A bibliography object.

        Returns:
            The dictionary of field value tracks with the below format:
            {'authors':
                {'author1':[timestamp1,timestamp2,timestamp3,...],
                 'author2':[timestamp2,timestamp3,timestamp7,...]},
             'titles':
                {'title1':[timestamp4,timestamp6,timestamp9,...],
                 'title2':[timestamp3,timestamp4,timestamp8,...]},
             ...}
        """
        if not self.revisions: self.get_revisions()
        tracks = {field:{field_value:[] for field_value in bibliography.field_values(field) if field_value} for field in fields}
        count = 0
        for revision in self.revisions:
            count += 1
            print(count)
            text = "".join(["".join(source.get_text()) for source in revision.get_further_reading() + revision.get_references()]).lower()
            #text = revision.get_text().lower()
            for field in tracks:
                for field_value in tracks[field]:
                    if field_value.lower() in text:
                        tracks[field][field_value].append(revision.timestamp.string)
        return tracks

    def track_phrases_in_article(self, phrase_lists):
        """
        Generates tracks of all phrases provided.

        Args:
            phrases: A list of phrase lists.
            
        Returns:
            The dictionary of phrases and their occurances:
            {"phrase1, phrase2, ...":
                {'phrase1':[timestamp1,timestamp2,timestamp3,...],
                 'phrase2':[timestamp2,timestamp3,timestamp7,...]
                 "..."},
            }
        """
        if not self.revisions: self.get_revisions()
        tracks = {"(" + ",".join(phrase_list)[:20] + "(...)" * (",".join(phrase_list)[10:] != "") + ")":{phrase:[] for phrase in phrase_list} for phrase_list in phrase_lists}
        count = 0
        for revision in self.revisions:
            count += 1
            print(count)
            #text = "".join(["".join(reference.itertext()) for reference in revision.get_references()]).lower()
            text = revision.get_text().lower()
            for phrase_list in tracks:
                for phrase in tracks[phrase_list]:
                    if phrase.lower() in text:
                        tracks[phrase_list][phrase].append(revision.timestamp.string)
        return tracks

    def write_track_to_file(self, track, directory):
        """
        Write track to JSON file.

        Args:
            track: A dictionary item with the below format:
                  (bibkey, {bibkey_value1:[timestamp1,timestamp2,timestamp3,...],
                            bibkey_value2:[timestamp4,timestamp6,timestamp9,...],
                            ...}).
            directory: The directory to which the file will be written.
        """
        if not self.revisions: self.get_revisions()
        bibkey = track[0]
        bibkey_value_dictionary = track[1]
        filename = self.name.lower() + "_wikipedia_revision_history_" + bibkey + ".txt"
        track = {bibkey_value:[timestamp for timestamp in bibkey_value_dictionary[bibkey_value]] for bibkey_value in bibkey_value_dictionary}
        if not exists(directory): makedirs(directory)
        with open(directory + sep + filename, "w") as file:
            dump(track, file)

    def plot_track_to_file(self, track, directory):
        """
        Plot track to file.

        Args:
            track: A dictionary item with the below format:
                  (bibkey, {bibkey_value1:[timestamp1,timestamp2,timestamp3,...],
                            bibkey_value2:[timestamp4,timestamp6,timestamp9,...],
                            ...}).
            directory: The directory to which the plot will be saved.
        """
        if not self.revisions: self.get_revisions()
        bibkey = track[0]
        bibkey_value_dictionary = track[1]
        plt.figure(figsize=(int(len(self.timestamps) * 0.15) + 10, 10), dpi=100)
        plt.title("Timeline of " + bibkey[0].upper() + bibkey[1:])
        plt.xticks(list(range(len(self.timestamps))), self.timestamps, rotation='vertical')
        plt.xlim((0, len(self.timestamps)))
        for bibkey_value in bibkey_value_dictionary:
            timestamps = bibkey_value_dictionary[bibkey_value]
            plt.plot([self.timestamps.index(timestamp) for timestamp in timestamps], [bibkey_value[:30] + "(...)" * (bibkey_value[30:] != "")] * len(timestamps), "o")
        plt.subplots_adjust(bottom=0.175, top=0.95, left=0.1, right=0.995)
        filename = self.name.lower() + "_wikipedia_revision_history_" + bibkey + ".png"
        if not exists(directory): makedirs(directory)
        plt.savefig(directory + sep + filename)

    def plot_revision_distribution_to_file(self, directory):
        """
        Plot the distribution of revisions across the entire revision timespan to file.
        Revisions are accumulated per month

        Args:
            directory: The directory to which the plot will be saved.
        """
        revisions = self.yield_revisions()
        revision = next(revisions, None)
        first_year = revision.timestamp.year
        while True:
            next_revision = next(revisions, None)
            if next_revision:
                revision = next_revision
            else:
                break
        final_year = revision.timestamp.year
        distribution = {}
        for year in range(first_year, final_year + 1):
            for month in range(1, 13):
                distribution[str(year) + "/" + str(month).rjust(2, "0")] = 0
        for revision in self.yield_revisions():
            distribution[str(revision.timestamp.year) + "/" + str(revision.timestamp.month).rjust(2, "0")] += 1

        plt.figure(figsize=(int(len(distribution) * 0.15), 10), dpi=150)
        plt.title(self.name + " Revision Distribition")
        plt.xlabel('month')
        plt.ylabel('number of revisions')
        plt.bar(list(range(len(distribution))), list(distribution.values()))
        plt.xticks(list(range(len(distribution))), list(distribution.keys()), rotation='vertical')
        plt.subplots_adjust(bottom=0.1, top=0.95, left=0.1, right=0.995)
        filename = self.name.lower() + "_wikipedia_revision_distribution" + ".png"
        if not exists(directory): makedirs(directory)
        plt.savefig(directory + sep + filename)

    def calculate_revision_size_difference(self):
        """
        Provides a list of size differences between all revisions on file.

        Returns:
            A list of n-1 integers for the size difference between all n revisions on file.
        """
        revisions = self.yield_revisions()
        size_differences = []
        
        revision = next(revisions)
        for next_revision in revisions:
            size_differences.append(next_revision.size - revision.size)
            revision = next_revision

        return size_differences

    def plot_revision_size_difference_to_file(self, directory):
        """
        Plot the change in size of each revision in comparison to the previous one to file.

        Args:
            directory: The directory to which the plot will be saved.
        """

        size_differences = [diff if abs(diff) < 5000 else 500 for diff in self.calculate_revision_size_difference()]

        plt.figure(figsize=(10, 2), dpi=1000)
        plt.title(self.name + " Revision Size Differences")
        plt.xlabel('index')
        plt.ylabel('bytes changed\n(changes > 4000 bytes cut)')
        plt.bar(list(range(len(size_differences))), size_differences)
        plt.xticks(list(range(len(size_differences))), list(range(len(size_differences))))
        plt.xticks([])
        filename = self.name.lower() + "_wikipedia_revision_size_differences" + ".png"
        if not exists(directory): makedirs(directory)
        plt.savefig(directory + sep + filename)
