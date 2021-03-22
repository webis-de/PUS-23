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

def calculate_data(filepath, strings, level, differs, preprocessor = None):

    with open(dirname(filepath) + sep + "CALCULATION.log", "a") as log_file:

        article = Article(filepath)

        log_file.write("Calculating diffs for " + article.name + " and sections '" + "', '".join(strings) + "'" + "\n")

        data = []

        prev_text = ""

        start = datetime.now()

        for revision in article.yield_revisions():

            log_file.write(str(revision.index + 1) + " " + str(revision.url) + "\n")
            print(revision.index + 1)

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

        log_file.write("TOTAL TIME: " + str(datetime.now() - start) + "\n")

        log_file.close()

        return data

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

def plot_size_and_reference_count_and_diffs(timesliced_data, filepath, article_name, section_name, differ_name, width, height):
    sizes = []
    reference_counts = []
    added_characters = []
    removed_characters = []
    timeslice_ticks = generate_annual_timeslice_ticks(timesliced_data, months=True)

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

    try:
        pcc = round(corr_coef(sizes, reference_counts), 3)
    except:
        pcc = "n/a"

    print("PCC:", pcc)
    print("Plotting " + article_name)

    reference_counts_color = "k"
    reference_counts_label = "NUMBER OF REFERENCES"

    sizes_color = "k"
    sizes_label = "MEAN CHARACTER COUNT"

    added_characters_color = "lightgray"

    removed_characters_color = "darkgray"

    fig, ax1 = plt.subplots(figsize = (width, height), dpi = 150)
    
    #x axis
    plt.xticks(list(range(len(timeslice_ticks))), timeslice_ticks, rotation=90)
    plt.margins(x=0.005)
    #reference counts
    ax1.plot(list(range(len(reference_counts))), reference_counts, label=reference_counts_label, color=reference_counts_color, linestyle=":")
    ax1.set_ylabel(reference_counts_label, color=reference_counts_color)
    ax1.tick_params('y', colors=reference_counts_color)
    ax1.set_ylim(ymin=0)
    #sizes
    ax2 = ax1.twinx()
    ax2.plot(list(range(len(sizes))), sizes, label=sizes_label, color=sizes_color)
    ax2.set_ylabel("CHARACTERS")
    ax2.tick_params('y')
    ax2.set_ylim(ymin=0)
    ax2.set_ylim(ymax=max(max(added_characters),max(removed_characters)))
    #added characters
    plt.bar(np.arange(len(added_characters)) - 0.15, added_characters, width=0.3, label="TOTAL NUMBER OF ADDED CHARACTERS", color=added_characters_color)
    #removed characters
    plt.bar(np.arange(len(removed_characters)) + 0.15, removed_characters, width=0.3, label="TOTAL NUMBER OF REMOVED CHARACTERS", color=removed_characters_color)

    plt.title(article_name + " " + section_name + " PCC: " + str(pcc))
    
    plt.subplots_adjust(bottom=0.1, top=0.975, left=0.01, right=0.999)
    
    fig.tight_layout()
    fig.legend(bbox_to_anchor=(0.95, 0.95), bbox_transform=ax2.transAxes)
    plt.savefig(filepath + "_section_revision_size_vs_reference_length_vs_diff.png")
    plt.close('all')

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
    
if __name__ == "__main__":

    preprocessor = Preprocessor("en")

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

    article_name = "CRISPR_gene_editing"
    article_lang = "en"
    section_name = "Intro"
    differ_name = "custom_differ"
    strings,level = sections[section_name]
    width = 30.0
    height = 10.0
    
    article_filepath = "../analysis/sections/TEST/" + article_name + "_" + article_lang
    section_filepath = article_filepath + "_" + section_name.lower()
    article_name = article_name.replace("_", " ")

    if not exists(section_filepath + "_diff_data.json"):
        data = calculate_data(article_filepath, strings, level, differs, preprocessor)
        save_data(data, section_filepath)
    else:
        data = load_data(section_filepath + "_diff_data.json")

    timesliced_data = timeslice_data(data, 2021, 2)
    
##    plot_diffs(data, section_filepath, section_name, width, height, article_name)    
##    plot_size_and_reference_count(timesliced_data, section_filepath, article_name, section_name)
    plot_size_and_reference_count_and_diffs(timesliced_data, section_filepath, article_name, section_name, differ_name, width, height)
