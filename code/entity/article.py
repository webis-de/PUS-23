from entity.revision import Revision
from entity.timestamp import Timestamp
from os.path import basename, exists, sep
from os import makedirs
import matplotlib.pyplot as plt
from json import loads, dump

class Article:
    """
    Reads line JSON file of revision history of Wikipedia article and
    allows tracking, saving and plotting of bibentry value and phrase occurances.

    Attributes:
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
        self.filename = basename(filepath)
        self.name = self.filename.replace(".","_")
        with open(filepath) as file:
            self.revisions = [Revision(revision["revid"],
                                       revision["parentid"],
                                       revision["url"],
                                       revision["user"],
                                       revision["userid"],
                                       revision["timestamp"],
                                       revision["size"],
                                       revision["html"],
                                       revision["comment"],
                                       revision["minor"],
                                       revision["index"])
                              for revision in [loads(line) for line in file.readlines()]]
        self.timestamps = [revision.timestamp_pretty_string() for revision in self.revisions]

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
        tracks = {field:{field_value:[] for field_value in bibliography.field_values(field) if field_value} for field in fields}
        for revision in self.revisions:
            for field in tracks:
                if field is "authors":
                    text = revision.get_text()
                else:
                    text = revision.get_text().lower()
                for field_value in tracks[field]:
                    if field_value in text:
                        tracks[field][field_value].append(revision.timestamp_pretty_string())
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
        tracks = {"(" + ",".join(phrase_list)[:20] + "(...)" * (",".join(phrase_list)[10:] != "") + ")":{phrase:[] for phrase in phrase_list} for phrase_list in phrase_lists}
        for revision in self.revisions:
            for phrase_list in tracks:
                for phrase in tracks[phrase_list]:
                    if phrase in revision.text.lower():
                        tracks[phrase_list][phrase].append(revision.timestamp_pretty_string())
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
        distribution = {}
        for year in range(self.revisions[0].get_year(), self.revisions[-1].get_year() + 1):
            for month in range(1, 13):
                distribution[str(year) + "/" + str(month).rjust(2, "0")] = 0
        for revision in self.revisions:
            distribution[str(revision.get_year()) + "/" + str(revision.get_month()).rjust(2, "0")] += 1

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
