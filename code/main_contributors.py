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

    if not exists(DIRECTORY): makedirs(DIRECTORY)

    if True:
        with open(DIRECTORY + sep + "revision_contributors.txt", "w") as txt_file, \
             open(DIRECTORY + sep + "revision_contributors.json", "w") as jsn_file:

            article = Article("../articles/2020-12-12/CRISPR_en")

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

            while revision.index < 200:

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
        with open(DIRECTORY + sep + "revision_contributors.json") as jsn_file:
            for line in jsn_file:
                versions.append(loads(line))

    editors = set()
    for revision in versions:
        for editor in revision:
            editors.add(editor)

    start = datetime.now()

    data = []

    for editor in editors:
        editor_data = []
        for revision in versions:
            editor_data.append(revision.get(editor, [0])[0])
        data.append(editor_data)
    editor_data = data[0]
    

    plt.figure(figsize=(5, 5), dpi=2000)
    plt.subplots_adjust(bottom=0, top=1, left=0, right=1)
    plt.margins(x=0, y=0)
    COLORS = plt.cm.get_cmap("hsv", len(editors))

    count = 0
    plt.bar(range(len(editor_data)), editor_data, width=1, color=COLORS(count))
    bottom = [0 for _ in editor_data]
    
    for new_editor_data in data[1:]:
        count += 1
        print(count)
        bottom = np.add(editor_data, bottom)
        plt.bar(range(len(new_editor_data)), new_editor_data, bottom=bottom, width=1, color=COLORS(count))
        editor_data = new_editor_data
    
    plt.savefig(DIRECTORY + sep + "revision_contributors.png")

    end = datetime.now()
    
    print("Plotting time:", end - start)
