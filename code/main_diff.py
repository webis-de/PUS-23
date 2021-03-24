import matplotlib.pyplot as plt
from article.article import Article
from article.revision.timestamp import Timestamp
from differ.lcs import Differ as custom_differ
from difflib import Differ as difflib_differ
from datetime import datetime
from json import load, loads, dump, dumps
from os.path import basename, dirname, exists, sep
from glob import glob
from urllib.parse import quote, unquote
from math import sqrt
from preprocessor.preprocessor import Preprocessor
import numpy as np
from utility.logger import Logger

def corr_coef(X,Y):
    mean_x = sum(X) / len(X)
    mean_y = sum(Y) / len(Y)

    Sxy = 0
    Sxx = 0
    Syy = 0
    for i in range (0, len(X)):
        Sxy += (X[i] - mean_x) * (Y[i] - mean_y)
        Sxx += (X[i] - mean_x)**2
        Syy += (Y[i] - mean_y)**2

    return Sxy / sqrt(Sxx * Syy)

def timeslice_data(data, FINAL_YEAR, FINAL_MONTH):
    first_timestamp = Timestamp(data[0]["revision_timestamp"])
    FIRST_YEAR, FIRST_MONTH = first_timestamp.year, first_timestamp.month
    timeslices = []
    for year in range(FIRST_YEAR, FINAL_YEAR + 1):
        for month in range(1, 13):
            if (year > FIRST_YEAR or month >= FIRST_MONTH) and \
               (year < FINAL_YEAR or month <= FINAL_MONTH):
                timeslices.append(str(month) + "/" + str(year))
    timesliced_data = {timeslice:[] for timeslice in timeslices}

    for index,item in enumerate(data, 1):
        timestamp = Timestamp(item["revision_timestamp"])
        timeslice = str(timestamp.month) + "/" + str(timestamp.year)
        
        if timeslice in timesliced_data:
            timesliced_data[timeslice].append(item)

    return timesliced_data

def generate_annual_timeslice_ticks(timeslices, months = False):
    timeslice_ticks = []
    for timeslice in timeslices:
        year = timeslice.rjust(7, "0") if months else timeslice.split("/")[-1]
        timeslice_ticks.append(year if year not in timeslice_ticks else "")
    return timeslice_ticks

def calculate_data(filepath, logger, strings, level, differs, preprocessor = None, problematic_revids = []):

    article = Article(filepath)

    logger.log("Calculating diffs for " + article.name + " and sections '" + "', '".join(strings) + "'" + "\n")

    data = []

    prev_text = ""

    start = datetime.now()

    for revision in article.yield_revisions():

        logger.log(str(revision.index + 1) + " " + str(revision.url) + "\n")

        if revision.revid in problematic_revids:
            logger.log("Blacklisted revid:",revision.revid)
            continue

        section_tree = revision.section_tree()

        section = section_tree.find(strings, True)
        text = section[0].get_text(level, include = ["p","li"], with_headings=True) if section else ""
        if preprocessor:
            text = preprocessor.preprocess(text, lower=False, stopping=False, sentenize=False, tokenize=True)[0]
        references = section[0].get_sources(revision.get_references(), level) if section else []

        diffs = {differ_name:list(differ.compare(prev_text, text))
                 for differ_name, differ in differs.items()}
        
        data.append(
            {"revision_timestamp":revision.timestamp.timestamp_string(),
             "revision_url":revision.url,
             "revision_index":revision.index,
             "revision_revid":revision.revid,
             "size":sum([len(item) for item in text]),
             "refcount":len(references),
             "diffs":{
                 differ_name:{
                     "added_characters":sum([len(item[2:]) for item in diff if item[0] == "+"]),
                     "removed_characters":sum([len(item[2:]) for item in diff if item[0] == "-"]),
                     "diff":diff} for differ_name, diff in diffs.items()
                 }
             }
            )

        prev_text = text

    logger.log("TOTAL TIME: " + str(datetime.now() - start) + "\n")

    return data

def plot_diffs(data, filepath, section_name, width, height, article_name):
    differ_names = list(data)[0]["diffs"].keys()

    for differ_name in differ_names:

        ticks = []
        for item in data:
            timestamp = Timestamp(item["revision_timestamp"])
            ticks.append(timestamp.string if
                         any([item["diffs"][differ_name]["added_characters"],
                              item["diffs"][differ_name]["removed_characters"]]) else "")

        added_characters = [item["diffs"][differ_name]["added_characters"] for item in data]
        removed_characters = [item["diffs"][differ_name]["removed_characters"] for item in data]
        sizes = [item["size"] for item in data]

        plt.figure(figsize=(width, height), dpi=150)
        plt.subplots_adjust(bottom=0.1, top=0.975, left=0.01, right=0.999)
        plt.margins(x=0)
        plt.bar(np.arange(len(added_characters)) - 0.15, added_characters, width=0.3, label="added characters")
        plt.bar(np.arange(len(removed_characters)) + 0.15, removed_characters, width=0.3, label="removed characters")
        plt.plot(list(range(len(sizes))), sizes, label="section size", color="green")
        plt.xticks(list(range(len(ticks))), ticks, rotation = 90)
        plt.title("Development of " + section_name + " Section in " + article_name)
        plt.legend()
        plt.savefig(filepath + "_section_analysis_" + differ_name + ".png")

def save_data(data, section_filepath):
    with open(section_filepath + "_diff_data.json", "w") as data_file:
        for line in data:
            data_file.write(dumps(line) + "\n")

def load_data(data_filepath):
    with open(data_filepath) as file:
        return [loads(line) for line in file]
"""
def plot_size_and_reference_count(timesliced_data, filepath, article_name, section_name):
    sizes = []
    reference_counts = []
    timeslice_ticks = generate_annual_timeslice_ticks(timesliced_data)

    prev_size = 0
    prev_reference_count = 0
    
    for data in timesliced_data.values():       
        try:
            sizes.append(sum([item["size"] for item in data])/len(data))
            prev_size = sizes[-1]
        except ZeroDivisionError:
            sizes.append(prev_size)
        try:
            reference_counts.append(sum([item["refcount"] for item in data])/len(data))
            prev_reference_count = reference_counts[-1]
        except ZeroDivisionError:
            reference_counts.append(prev_reference_count)  

    try:
        pcc = round(corr_coef(sizes, reference_counts), 3)
    except:
        pcc = "n/a"

    print("PCC:", pcc)
    print("Plotting " + article_name)

    reference_counts_color = "y"
    reference_counts_label = "References in Section " + section_name + " in " + article_name

    sizes_color = "b"
    sizes_label = "Size of Section " + section_name + " in " + article_name

    fig, ax1 = plt.subplots()
    plt.xticks(list(range(len(timeslice_ticks))), timeslice_ticks, rotation=90)
    ax1.plot(list(range(len(reference_counts))), reference_counts, label=reference_counts_label, color=reference_counts_color)
    ax1.set_ylabel(reference_counts_label, color=reference_counts_color)
    ax1.tick_params('y', colors=reference_counts_color)
    ax2 = ax1.twinx()
    ax2.plot(list(range(len(sizes))), sizes, label=sizes_label, color=sizes_color)
    ax2.set_ylabel(sizes_label, color=sizes_color)
    ax2.tick_params('y', colors=sizes_color)
    ax1.set_ylim(ymin=0)
    ax2.set_ylim(ymin=0)
    #plt.subplots_adjust(bottom=0.12, top=0.98, left=0.12, right=0.88)
    plt.title("PCC: " + str(pcc))
    fig.tight_layout()
    plt.savefig(filepath + "_section_revision_size_vs_reference_length.png")
    plt.close('all')
"""

def handle_timesliced_data(timesliced_data):
    sizes = []
    reference_counts = []
    added_characters = []
    removed_characters = []
    timeslice_ticks = [item if index%3 == 0 else "" for index,item in enumerate(generate_annual_timeslice_ticks(timesliced_data, True))]

    prev_size = 0
    prev_reference_count = 0
    
    for data in timesliced_data.values():       
        try:
            sizes.append(sum([item["size"] for item in data])/len(data))
            prev_size = sizes[-1]
        except ZeroDivisionError:
            sizes.append(prev_size)
        try:
            reference_counts.append(sum([item["refcount"] for item in data])/len(data))
            prev_reference_count = reference_counts[-1]
        except ZeroDivisionError:
            reference_counts.append(prev_reference_count)
        try:
            added_characters.append(sum([item["diffs"][differ_name]["added_characters"] for item in data]))
        except ZeroDivisionError:
            added_characters.append(0)
        try:
            removed_characters.append(sum([item["diffs"][differ_name]["removed_characters"] for item in data]))
        except ZeroDivisionError:
            removed_characters.append(0)
    return sizes, reference_counts, added_characters, removed_characters, timeslice_ticks

def plot_size_and_reference_count_and_diffs(timesliced_datasets, logger, directory, section_name, differ_name):

    fig = plt.figure(figsize=(30,6))
    axs = [plt.subplot2grid((12, 48), (0, 0), colspan=39, rowspan=12),
           plt.subplot2grid((12, 48), (0, 41), colspan=6, rowspan=12)]

    handle_yaxis = True
    reference_max = None
    sizes_max = None

    for timesliced_data, ax1 in zip(timesliced_datasets, axs):
        
        sizes, reference_counts, added_characters, removed_characters, timeslice_ticks = handle_timesliced_data(timesliced_datasets[timesliced_data])

        if handle_yaxis:
            reference_max = max(reference_counts)
            sizes_max = max(max(added_characters),max(removed_characters))

        try:
            pcc = round(corr_coef(sizes, reference_counts), 3)
        except:
            pcc = "n/a"

        logger.log("PCC:", pcc)
        logger.log("Plotting " + article_name + " " + section_name)

        reference_counts_color = "k"
        reference_counts_label = "NUMBER OF REFERENCES"

        sizes_color = "k"
        sizes_label = "MEAN CHARACTER COUNT"

        added_characters_color = "lightgray"
        added_characters_label = "TOTAL NUMBER OF ADDED CHARACTERS"

        removed_characters_color = "darkgray"
        removed_characters_label = "TOTAL NUMBER OF REMOVED CHARACTERS"
        
        #x ticks
        ax1.set_xticks(list(range(len(timeslice_ticks))))
        ax1.set_xticklabels(timeslice_ticks, rotation=90, fontsize="medium")
        #reference counts
        ax1.margins(x=0.005)
        ax1.plot(list(range(len(reference_counts))), reference_counts, label=reference_counts_label, color=reference_counts_color, linestyle=":")
        if handle_yaxis: ax1.set_ylabel(reference_counts_label, color=reference_counts_color, fontsize="xx-large")
        ax1.tick_params(colors=reference_counts_color)
        ax1.set_ylim(ymin=0, ymax=reference_max)
        #sizes
        ax2 = ax1.twinx()
        ax2.margins(x=0.005)
        ax2.plot(list(range(len(sizes))), sizes, label=sizes_label, color=sizes_color)
        if not handle_yaxis: ax2.set_ylabel("CHARACTERS", color=sizes_color, fontsize="xx-large")
        ax2.tick_params(colors=sizes_color)
        ax2.set_ylim(ymin=0, ymax=sizes_max)
        #added characters
        plt.bar(np.arange(len(added_characters)) - 0.2, added_characters, width=0.4, label=added_characters_label, color=added_characters_color)
        #removed characters
        plt.bar(np.arange(len(removed_characters)) + 0.2, removed_characters, width=0.4, label=removed_characters_label, color=removed_characters_color)

        plt.title("PCC: " + str(pcc), fontsize="xx-large")

        handle_yaxis = False
        
    plt.subplots_adjust(bottom=0.15, top=0.925, left=0.03, right=0.98)
    fig.tight_layout()
    #fig.legend(bbox_to_anchor=(0.01, 0.95), bbox_transform=ax2.transAxes, fontsize="large")
    plt.savefig(directory + sep + "_".join(timesliced_datasets.keys()).replace(" ","_") + "_" + section_name  + "_" + "section_revision_size_vs_references_vs_diffs.png")
    plt.close('all')
    
if __name__ == "__main__":

    from problematic_revids import problematic_revids_CRISPR_en, problematic_revids_CRISPR_gene_editing_en

    language = "en"

    preprocessor = Preprocessor(language)

    articles = (
        ("CRISPR",16.5,True,problematic_revids_CRISPR_en),
        ("CRISPR_gene_editing",3.5,False,problematic_revids_CRISPR_gene_editing_en)
        )

    sections = {"Intro":([""],0),
                "All":([""],10),
                "History":(["History",
                            "Discovery and properties",
                            "Discovery of CRISPR"],
                           10),
                "Application":(["The significance for evolution and possible applications",
                                "Possible applications",
                                "Applications"],
                                10)
                }

    differs = {"difflib_differ":difflib_differ(),"custom_differ":custom_differ()}

    directory = "../analysis/sections/TEST1/"

    logger = Logger(directory)

    for section_name in ["All","Intro","History","Application"]:

        timesliced_datasets = {}
        
        for article_name,width,legend,problematic_revids in articles:
            
            differ_name = "custom_differ"
            strings,level = sections[section_name]
            height = 6
            
            article_filepath = directory + article_name + "_" + language
            section_filepath = article_filepath + "_" + section_name.lower()

            if not exists(section_filepath + "_diff_data.json"):
                data = calculate_data(article_filepath, logger, strings, level, differs, preprocessor, [])
                save_data(data, section_filepath)
            else:
                data = load_data(section_filepath + "_diff_data.json")

            timesliced_datasets[article_name.replace("_", " ")] = timeslice_data(data, 2021, 2)
            
            #plot_diffs(data, section_filepath, section_name, width, height, article_name)    
            #plot_size_and_reference_count(timesliced_data, section_filepath, article_name, section_name)
        plot_size_and_reference_count_and_diffs(timesliced_datasets, directory, logger, section_name, differ_name)