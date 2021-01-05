from argparse import ArgumentParser
from article.article import Article
from contribution.contribution import Contribution
from pprint import pprint
from json import dumps, loads
from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np
from os.path import exists, sep
from os import makedirs

def calculate_contributions(article_directory, article_title, text_file, json_file):

    contributions = []
    
    article = Article(article_directory + sep + article_title)

    revisions = article.yield_revisions()

    start = datetime.now()

    revision = next(revisions, None)
    contribution = Contribution(revision.index, revision.url, revision.size, revision.get_text(), revision.user, revision.userid)
    contribution.diff()
    editors = contribution.editors()

    JSN = contribution.json(editors)
    TBL = contribution.table(editors)

    contributions.append(JSN)
    json_file.write(dumps(JSN) + "\n")
    text_file.write(TBL)

    while revision.index < 2000:

        print(revision.index)
        
        revision = next(revisions, None)

        if revision:
            
            next_contribution = Contribution(revision.index, revision.url, revision.size, revision.get_text(), revision.user, revision.userid)
            next_contribution.diff(contribution)
            next_editors = contribution.editors()

            JSN = next_contribution.json(next_editors)
            TBL = next_contribution.table(next_editors)

            contributions.append(JSN)
            json_file.write(dumps(JSN) + "\n")
            text_file.write(TBL)

            contribution = next_contribution

    end = datetime.now()

    print("Calculation time:", end - start)

    return contributions

def get_contributions(output_directory, article_title, article_directory, basename):
    contributions = []

    BASENAME = output_directory + sep + article_title + "_revision_contributors"

    if not exists(output_directory): makedirs(output_directory)

    if not exists(basename + ".json"):
        with open(basename + ".txt", "w") as text_file, \
             open(basename + ".json", "w") as json_file:
            contributions = calculate_contributions(article_directory, article_title, text_file, json_file)
    else:
        with open(basename + ".json") as jsn_file:
            for line in jsn_file:
                contributions.append(loads(line))

    return contributions[:998] + contributions[999:2000]

def plot_contributions(contributions, basename, threshold = 0.0):
    editors = sorted(set([editor for contribution in contributions for editor in contribution]))
    significant_editors = sorted(set([editor for contribution in contributions for editor in contribution
                                      if contribution[editor]["relative"] >= threshold]))
    print("Number of editors:", len(editors))
    print("Number of significant editors with contribution greater", threshold, "in any revision: ", len(significant_editors))

    editors = significant_editors

    data = [[contribution.get(editor, {}).get("absolute", 0)
             if contribution.get(editor, {}).get("relative", 0) >= threshold
             else 0
             for contribution in contributions]
            for editor in editors]

    start = datetime.now()

    plt.figure(figsize=(5, 5), dpi=2000)
    plt.subplots_adjust(bottom=0, top=1, left=0, right=1)
    plt.margins(x=0, y=0)
    COLORS = plt.cm.get_cmap("hsv", len(editors))

    bottom = [0 for _ in range(len(contributions))]
    
    for count, editor_data in enumerate(data):
        plt.bar(range(len(editor_data)), editor_data, bottom=bottom, width=1, color=COLORS(count))
        bottom = np.add(editor_data, bottom)
        print(count + 1)
    
    plt.savefig(basename + ".png")

    end = datetime.now()

    print("Plotting time:", end - start)

if __name__ == "__main__":
    
    output_directory = ".." + sep + "contributors_test"
    article_directory = "../articles/2020-10-24"
    article_title = "CRISPR_en"
    basename = output_directory + sep + article_title + "_revision_contributors"

    contributions = get_contributions(output_directory,
                                      article_title,
                                      article_directory,
                                      basename)
    plot_contributions(contributions, basename, 0.05)
    
