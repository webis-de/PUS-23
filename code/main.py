from article.article import Article
from differ.lcs import Differ as custom_differ
from difflib import Differ as difflib_differ
import matplotlib.pyplot as plt
from datetime import datetime
from json import dumps
import numpy as np

titles = {"CRISPR_gene_editing_en":25,"CRISPR_en":100}
sections = ["History", "Discovery and properties", "Discovery of CRISPR"]
differs = {"difflib_differ":difflib_differ(),"custom_differ":custom_differ()}

for title, graph_width in titles.items():
    for differ_name, differ in differs.items(): 
        article = Article("../articles/2021-03-01/" + title)

        revision_urls = []
        timestamps_for_plotting = []
        timestamps = []
        added_characters = []
        removed_characters = []
        sizes = []
        diffs = []

        revision_iterator = article.yield_revisions()

        old_string = ""
        revision = next(revision_iterator, None)

        while revision:
            print(revision.index)
            print(revision.url)
            timestamps.append(revision.timestamp.string)
            revision_urls.append(revision.url)
            section_tree = revision.section_tree()
            section = section_tree.find(strings = sections, lower = True)
            new_string = section[0].get_text(10) if section else ""
            diff = differ.compare(old_string, new_string)
            timestamp = str(revision.timestamp.month).rjust(2,"0") + "/" + str(revision.timestamp.year)
            timestamps_for_plotting.append("" if timestamp in timestamps_for_plotting else timestamp)
            added = 0
            removed = 0
            dif = []
            for item in diff:
                if item[0] == "+":
                    added += 1
                if item[0] == "-":
                    removed += 1
                dif.append(item)
            added_characters.append(added)
            removed_characters.append(removed)
            sizes.append(len(new_string))
            diffs.append(dif)
            print("="*50)
            old_string = new_string
            revision = next(revision_iterator, None)

        plt.figure(figsize=(graph_width, 5), dpi=250)
        plt.subplots_adjust(bottom=0.15, top=0.95, left=0.02, right=0.99)
        plt.margins(x=0)
        plt.bar(np.arange(len(added_characters)) - 0.15, added_characters, width=0.3, label="added characters")
        plt.bar(np.arange(len(removed_characters)) + 0.15, removed_characters, width=0.3, label="removed characters")
        plt.plot(list(range(len(sizes))), sizes, label="section size", color="green")
        plt.xticks(list(range(len(timestamps_for_plotting))), timestamps_for_plotting, rotation = 90)
        plt.title("Length of Sections " + "/".join(sections) + " in " + article.name.replace("_"," ")[:-3])
        plt.legend()
        plt.savefig(article.name + "_history_section_analysis_" + differ_name + ".png")
        with open(article.name + "_history_section_analysis_" + differ_name + ".json", "w") as file:
            file.write(dumps({"revision_urls":revision_urls,
                              "timestamps":timestamps,
                              "added_characters":added_characters,
                              "removed_characters":removed_characters,
                              "sizes":sizes,
                              "diffs":diffs}))

