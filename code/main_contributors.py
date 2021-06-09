from argparse import ArgumentParser
from article.article import Article
from differ.differ import Differ
from preprocessor.preprocessor import Preprocessor
from contribution.contribution import Contribution
from pprint import pprint
from json import dumps, load, loads
from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np
from os.path import exists, sep
from os import makedirs

##################################################################################
# This file serves as an entry point to analyse Wikipedia articles contributions.#
##################################################################################

def length_diff(text, previous_text):
    return len(text)/len(previous_text)

def calculate_contributions(article_title,
                            article_directory,
                            section_strings,
                            section_level,
                            problematic_revids,
                            text_file,
                            json_file):

    differ = Differ()
    preprocessor = Preprocessor("en")

    contributions = []
    
    article = Article(article_directory + sep + article_title)

    revisions = article.yield_revisions()

    start = datetime.now()

    revision = next(revisions, None)
    sections = revision.section_tree().find(section_strings, lower=True)
    text = sections[0].get_text(section_level, include = ["p","li"], with_headings=True) if sections else ""
    previous_text = preprocessor.preprocess(text, lower=False, stopping=False, sentenize=False, tokenize=True)[0]
    previous_contribution = Contribution(differ, revision.index, revision.url, len(previous_text), previous_text, revision.user, revision.userid)
    previous_contribution.diff()
    editors = previous_contribution.editors()

    JSN = previous_contribution.json(editors)
    TBL = previous_contribution.table(editors)

    contributions.append(JSN)
    json_file.write(dumps(JSN) + "\n")
    text_file.write(TBL)

    while revision and revision.index < 2000:
        
        revision = next(revisions, None)

        if revision.revid in problematic_revids:
            print(revision.index, "- skipping revid", revision.revid)
            continue
        
        sections = revision.section_tree().find(section_strings, lower=True)
        text = sections[0].get_text(section_level, include = ["p","li"], with_headings=True) if sections else ""

        if revision:
            text = preprocessor.preprocess(text, lower=False, stopping=False, sentenize=False, tokenize=True)[0]
            
            contribution = Contribution(differ, revision.index, revision.url, len(text), text, revision.user, revision.userid)
            contribution.diff(previous_contribution)
            editors = contribution.editors()

            JSN = contribution.json(editors)
            TBL = contribution.table(editors)

            print(revision.index)

            contributions.append(JSN)
            json_file.write(dumps(JSN) + "\n")
            text_file.write(TBL)

            previous_contribution = contribution
            previous_text = text

    end = datetime.now()

    print("Calculation time:", end - start)

    return contributions

def get_contributions(output_directory,
                      article_title,
                      article_directory,
                      section_strings,
                      section_level,
                      problematic_revids,
                      basename):
    contributions = []

    BASENAME = output_directory + sep + article_title + "_revision_contributors"

    if not exists(output_directory): makedirs(output_directory)

    if not exists(basename + ".json"):
        with open(basename + ".txt", "w") as text_file, \
             open(basename + ".json", "w") as json_file:
            contributions = calculate_contributions(article_title,
                                                    article_directory,
                                                    section_strings,
                                                    section_level,
                                                    problematic_revids,
                                                    text_file,
                                                    json_file)
    else:
        with open(basename + ".json") as jsn_file:
            for line in jsn_file:
                contributions.append(loads(line))

    return contributions

def export_legend(legend, filename):
    fig  = legend.figure
    fig.canvas.draw()
    bbox  = legend.get_window_extent().transformed(fig.dpi_scale_trans.inverted())
    fig.savefig(filename, dpi="figure", bbox_inches=bbox)

def plot_contributions(contributions, basename, threshold = "0.00"):
    editors = sorted(set([editor for contribution in contributions for editor in contribution]))
    significant_editors = sorted(set([editor for contribution in contributions for editor in contribution
                                      if contribution[editor]["relative"] >= float(threshold)]))
    print("Number of editors:", len(editors))
    print("Number of significant editors with contribution greater", threshold, "in any revision: ", len(significant_editors))

    editors = significant_editors

    data = [[contribution.get(editor, {}).get("absolute", 0)
            if contribution.get(editor, {}).get("relative", 0) >= float(threshold)
            else 0
            for contribution in contributions]
            for editor in editors]

    start = datetime.now()

    plt.figure(figsize=(5, 5), dpi=600)
    plt.subplots_adjust(bottom=0, top=1, left=0, right=1)
    plt.margins(x=0, y=0)
    colors = plt.cm.get_cmap("hsv", len(editors))
    #colormap = {editors[i]:colors(i) for i in range(len(editors))}

    bottom = [0 for _ in range(len(contributions))]
    handles = []
    for count, editor_data in enumerate(data):
        handles += plt.bar(range(len(editor_data)), editor_data, bottom=bottom, width=1, color=colors(count))
        bottom = np.add(editor_data, bottom)
        print(count + 1)
    
    plt.savefig(basename + "_" + threshold + ".png")
    plt.close('all')
    export_legend(
        plt.legend(
            [plt.Rectangle((0,0),1,1, color=colors(editors.index(editor))) for editor in editors],
            editors,
            loc=3),
        basename + "_" + threshold + "_legend" + ".png")
    
    end = datetime.now()

    print("Plotting time:", end - start)

if __name__ == "__main__":
    
    sections = {"Intro":([""],0),
                "All":([""],10),
                "History":(["History",
                            "Discovery and properties",
                            "Discovery of CRISPR"],
                           10),
                "Application":(["The significance for evolution and possible applications",
                                "Possible applications",
                                "Applications"],
                                10),
                "NO_SECTION_TREE":([],0)
                }

    section_name = "Application"
    section_strings,section_level = sections[section_name]
    threshold = "0.05"
    
    article_directory = "../articles/2021-03-01"
    article_title = "CRISPR_en"
    output_directory = "../analysis/contributors/" + article_title
    basename = output_directory + sep + article_title + "_" + section_name.lower() + "_section_editor_contributions"
    problematic_revids = [item[0] for item in load(open("../data/problematic_revids.json"))[article_title]]

    contributions = get_contributions(output_directory,
                                      article_title,
                                      article_directory,
                                      section_strings,
                                      section_level,
                                      problematic_revids,
                                      basename)
    plot_contributions(contributions[:1589] + contributions[1590:], basename, threshold)
    
