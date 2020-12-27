from argparse import ArgumentParser
from article.article import Article
from contributors.contributors import Contributors
from pprint import pprint
from json import dumps, loads
from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np
from os.path import exists, sep
from os import makedirs

if __name__ == "__main__":

    versions = []

    DIRECTORY = ".." + sep + "contributors"

    TITLE = "CRISPR_en"

    BASENAME = DIRECTORY + sep + TITLE + "_revision_contributors"

    article = Article("../articles/2020-10-24/" + TITLE)

    if not exists(DIRECTORY): makedirs(DIRECTORY)

    if not exists(BASENAME + ".json"):
        with open(BASENAME + ".txt", "w") as txt_file, \
             open(BASENAME + ".json", "w") as jsn_file:

            revisions = article.yield_revisions()

            start = datetime.now()

            revision = next(revisions, None)
            txt_file.write(str(revision.index) + " " + revision.url + " " + "\n")
            contributors = Contributors(revision.get_text())
            contributors.align(revision.user)
            contributions = contributors.contributions()
            jsn_file.write(dumps(contributors.contributions_json(contributions)) + "\n")
            txt_file.write(contributors.contributions_table(contributions))

            versions.append(contributors.contributions_json(contributions))

            while revision.index < 100:

                print(revision.index)
                
                txt_file.write("="*100 + "\n")
                revision = next(revisions, None)

                if revision:
                    txt_file.write(str(revision.index) + " " + revision.url + " " + "\n")
                    next_contributors = Contributors(revision.get_text())
                    next_contributors.align(revision.user, contributors)
                    next_contributions = contributors.contributions()
                    jsn_file.write(dumps(next_contributors.contributions_json(next_contributions)) + "\n")
                    txt_file.write(next_contributors.contributions_table(next_contributions))

                    versions.append(next_contributors.contributions_json(next_contributions))
                    
                    contributors = next_contributors

            end = datetime.now()

            print("Calculation time:", end - start)
    else:
        with open(BASENAME + ".json") as jsn_file:
            for line in jsn_file:
                versions.append(loads(line))

    #versions = versions[:100]

    editors = set([editor for version in versions for editor in version])
    print("Number of editors:", len(editors))

    data = [[version.get(editor, [0])[0] for version in versions] for editor in editors]

    start = datetime.now()

    plt.figure(figsize=(5, 5), dpi=1000)
    plt.subplots_adjust(bottom=0, top=1, left=0, right=1)
    plt.margins(x=0, y=0)
    COLORS = plt.cm.get_cmap("hsv", len(editors))

    editor_data = data[0]
    editor_count = 0
    plt.bar(range(len(editor_data)), editor_data, width=1, color=COLORS(editor_count))
    bottom = [0 for _ in editor_data]
    
    for new_editor_data in data[1:]:
        editor_count += 1
        bottom = np.add(editor_data, bottom)
        plt.bar(range(len(new_editor_data)), new_editor_data, bottom=bottom, width=1, color=COLORS(editor_count))
        editor_data = new_editor_data
        print(editor_count)
    
    plt.savefig(BASENAME + ".png")

    end = datetime.now()
    
    print("Plotting time:", end - start)
