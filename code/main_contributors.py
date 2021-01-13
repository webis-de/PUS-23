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

def length_diff(text, previous_text):
    return len(text)/len(previous_text)

def calculate_contributions(article_directory, article_title, text_file, json_file):

    contributions = []
    
    article = Article(article_directory + sep + article_title)

    revisions = article.yield_revisions()

    start = datetime.now()

    revision = next(revisions, None)
    previous_text = revision.get_wikitext()
    previous_contribution = Contribution(revision.index, revision.url, revision.size, previous_text, revision.user, revision.userid)
    previous_contribution.diff()
    editors = previous_contribution.editors()

    JSN = previous_contribution.json(editors)
    TBL = previous_contribution.table(editors)

    contributions.append(JSN)
    json_file.write(dumps(JSN) + "\n")
    text_file.write(TBL)

    while revision.index < 2000:
        
        revision = next(revisions, None)

        if revision:

            text = revision.get_wikitext()
            
            contribution = Contribution(revision.index, revision.url, revision.size, text, revision.user, revision.userid)
            contribution.diff(previous_contribution)
            editors = contribution.editors()

            JSN = contribution.json(editors)
            TBL = contribution.table(editors)

            if length_diff(text, previous_text) < 0.1:
                print(revision.index, "Revision considerably shorter: skipping.")
                text_file.write("Revision considerably shorter: skipping." + "\n")
                text_file.write(TBL)
                continue
            elif length_diff(text, previous_text) > 10:
                print(revision.index, "Revision considerably longer: skipping.")
                text_file.write("Revision considerably longer: skipping." + "\n")
                text_file.write(TBL)
                continue
            else:
                print(revision.index)

                contributions.append(JSN)
                json_file.write(dumps(JSN) + "\n")
                text_file.write(TBL)

                previous_contribution = contribution
                previous_text = text

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

    return contributions

def plot_contributions(contributions, basename, threshold = 0.0):
    editors = sorted(set([editor for contribution in contributions for editor in contribution]))
    significant_editors = sorted(set([editor for contribution in contributions for editor in contribution
                                      if contribution[editor]["relative"] >= threshold]))
    print("Number of editors:", len(editors))
    print("Number of significant editors with contribution greater", threshold, "in any revision: ", len(significant_editors))

    editors = significant_editors

    data = [(editor, [contribution.get(editor, {}).get("absolute", 0)
                      if contribution.get(editor, {}).get("relative", 0) >= threshold
                      else 0
                      for contribution in contributions])
            for editor in editors]

    start = datetime.now()

    plt.figure(figsize=(5, 5), dpi=2000)
    plt.subplots_adjust(bottom=0, top=1, left=0, right=1)
    plt.margins(x=0, y=0)
    COLORS = {editor:color for editor,color in zip(editors,plt.cm.get_cmap("hsv", len(editors)))}

    bottom = [0 for _ in range(len(contributions))]
    
    for count, editor_data in enumerate(data):
        editor = editor_data[0]
        contribution = editor_data[1]
        plt.bar(range(len(contribution)), contribution, bottom=bottom, width=1, color=COLORS[editor])
        bottom = np.add(editor_data, bottom)
        print(count + 1)
    
    plt.savefig(basename + ".png")

    end = datetime.now()

    print("Plotting time:", end - start)

if __name__ == "__main__":
    
    output_directory = ".." + sep + "contributors_test_wikitext"
    article_directory = "../articles/no_html"
    article_title = "CRISPR_en"
    basename = output_directory + sep + article_title + "_revision_contributors"

    contributions = get_contributions(output_directory,
                                      article_title,
                                      article_directory,
                                      basename)
    plot_contributions(contributions, basename, 0.05)
    
