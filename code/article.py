from xmltodict import parse
from json import loads
from datetime import datetime
from json import dump
from revision import Revision
from timestamp import Timestamp
from os.path import basename, exists, sep
from os import makedirs
import matplotlib.pyplot as plt

class Article:
    """
    Reads XML file of revision history of Wikipedia article and
    allows tracking, saving and plotting of bibentry value occurances.

    Attributes:
        filename: The name of the XML file.
        name: The name of the article.
        revisions: The individual revisions in the XML tree.
        timestamps: The timestamps of all revisions.
    """
    def __init__(self, filepath):
        """
        Args:
            filepath: The path to the XML or JSON file.
        """
        self.filename = basename(filepath)
        self.name = self.filename.replace(".","_")
        if ".xml" in filepath:
            with open(filepath) as xml_file:
                self.revisions = [Revision(revision[1].get("id"),
                                           revision[1].get("text",{}).get("#text",""),
                                           Timestamp(revision[1].get("timestamp")),
                                           revision[0])
                                  for revision in enumerate(parse(xml_file.read())["mediawiki"]["page"]["revision"])]
            self.timestamps = [revision.timestamp.string for revision in self.revisions]
        if ".json" in filepath:
            with open(filepath) as json_file:
                self.revisions = [Revision(revision[1].get("id"),
                                           revision[1].get("text",{}).get("#text",""),
                                           Timestamp(revision[1].get("timestamp")),
                                           revision[0])
                                  for revision in enumerate([loads(line) for line in json_file.readlines()])]
            self.timestamps = [revision.timestamp.string for revision in self.revisions]                    

    def track_bibkeys_in_article(self, bibkeys, bibliography):
        """
        Generates tracks of all bibkey values of all bibkeys in bibliography provided.

        Args:
            bibkeys: A list of bibkeys.
            bibliography: A bibliography object.

        Returns:
            The dictionary of bibkey tracks with below format:
            {'authors':
                {'author1':[timestamp1,timestamp2,timestamp3,...],
                 'author2':[timestamp2,timestamp3,timestamp7,...]},
             'titles':
                {'title1':[timestamp4,timestamp6,timestamp9,...],
                 'title2':[timestamp3,timestamp4,timestamp8,...]},
             ...}
        """
        tracks = {bibkey:{bibkey_value:[] for bibkey_value in bibliography.bibkey_values(bibkey) if bibkey_value} for bibkey in bibkeys}
        for revision in self.revisions:
            for bibkey in tracks:
                if bibkey is "authors":
                    text = revision.text
                else:
                    text = revision.text.lower()
                for bibkey_value in tracks[bibkey]:
                    if bibkey_value in text:
                        tracks[bibkey][bibkey_value].append(revision.timestamp)
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
        tracks = {"(" + ",".join(phrase_list) + ")":{phrase:[] for phrase in phrase_list} for phrase_list in phrase_lists}
        for revision in self.revisions:
            for phrase_list in tracks:
                for phrase in tracks[phrase_list]:
                    if phrase in revision.text.lower():
                        tracks[phrase_list][phrase].append(revision.timestamp)
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
        track = {bibkey_value:[timestamp.string for timestamp in bibkey_value_dictionary[bibkey_value]] for bibkey_value in bibkey_value_dictionary}
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
            plt.plot([self.timestamps.index(timestamp.string) for timestamp in timestamps], [bibkey_value[:30] + "(...)" * (bibkey_value[30:] != "")] * len(timestamps), "o")
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
        for year in range(self.revisions[0].timestamp.datetime.year, self.revisions[-1].timestamp.datetime.year + 1):
            for month in range(1, 13):
                distribution[str(year) + "/" + str(month).rjust(2, "0")] = 0
        for revision in self.revisions:
            distribution[str(revision.timestamp.datetime.year) + "/" + str(revision.timestamp.datetime.month).rjust(2, "0")] += 1

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
        
