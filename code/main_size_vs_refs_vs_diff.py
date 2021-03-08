import matplotlib.pyplot as plt
from article.article import Article
from article.revision.timestamp import Timestamp
from differ.lcs import Differ as custom_differ
from difflib import Differ as difflib_differ
from datetime import datetime
from json import load, dump
from os.path import basename, exists
from glob import glob
from urllib.parse import quote, unquote
from math import sqrt
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
    first_timestamp = Timestamp(data[0]["timestamp"])
    FIRST_YEAR, FIRST_MONTH = first_timestamp.year, first_timestamp.month
    timeslices = []
    for year in range(FIRST_YEAR, FINAL_YEAR + 1):
        for month in range(1, 13):
            if (year > FIRST_YEAR or month >= FIRST_MONTH) and \
               (year < FINAL_YEAR or month <= FINAL_MONTH):
                timeslices.append(str(month) + "/" + str(year))
    timesliced_data = {timeslice:[] for timeslice in timeslices}

    for index,item in enumerate(data, 1):
        timestamp = Timestamp(item["timestamp"])
        timeslice = str(timestamp.month) + "/" + str(timestamp.year)
        
        if index % 100 == 0: print(index)
        if timeslice in timesliced_data:
            timesliced_data[timeslice].append(item)

    return timesliced_data

def generate_annual_timeslice_ticks(timeslices):
    timeslice_ticks = []
    for timeslice in timeslices:
        year = timeslice.split("/")[-1]
        timeslice_ticks.append(year if year not in timeslice_ticks else "")
    return timeslice_ticks

def generate_articlename(filepath):
    return "'" + unquote(basename(filepath)).replace("_", " ")[:-3] + "'"

def calculate_data(filepath, section_name, sections, differs):

    articletitle = generate_articlename(filepath)

    print("Calculating diffs for " + articletitle)

    data = []
    
    article = Article(filepath)

    prev_text = ""

    for revision in article.yield_revisions():

        if (revision.index + 1) % 100 == 0: print(revision.index + 1)

        section_tree = revision.section_tree()

        if section_name:
            section = section_tree.find(sections[section_name] if section_name else [""], True)
            text = section[0].get_text(10) if section else ""
        else:
            text = revision.get_text()

        diffs = {differ_name:list(differ.compare(prev_text, text))
                 for differ_name, differ in differs.items()} if section_name else {}
        
        data.append(
            {"timestamp":revision.timestamp_string(),
             "revision_url":revision.url,
             "revision_index":revision.index,
             "revision_revid":revision.revid,
             "size":len(text) if section_name else revision.size,
             "refcount":len(revision.get_references() + revision.get_further_reading()),
             "diffs":{
                 differ_name:{
                     "added_characters":len([item for item in diff if item[0] == "+"]),
                     "removed_characters":len([item for item in diff if item[0] == "-"]),
                     "diff":diff} for differ_name, diff in diffs.items()
                 }
             }
            )

        prev_text = text

    return data

def plot_size_and_reference_count(timesliced_data, filepath):
    articletitle = generate_articlename(filepath)
    
    sizes = []
    reference_counts = []
    timeslice_ticks = generate_annual_timeslice_ticks(timesliced_data)

    prev_size = 0
    prev_reference_count = 0
    
    for timeslice, data in timesliced_data.items():
            
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
    print("Plotting " + articletitle)

    reference_counts_color = "y"
    reference_counts_label = f"References in {articletitle}"

    sizes_color = "b"
    sizes_label = f"Size of {articletitle}"

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
    plt.savefig(filepath + "_revision_size_vs_reference_length.png")
    plt.close('all')

    return sizes, reference_counts

def plot_diffs(data, filepath):
    articletitle = generate_articlename(filepath)

    differ_names = list(data)[0]["diffs"].keys()
    ticks = []
    for item in data:
        timestamp = Timestamp(item["timestamp"])
        timestamp = str(timestamp.month).rjust(2,"0") + "/" + str(timestamp.year)
        ticks.append(timestamp if timestamp not in ticks else "")

    for differ_name in differ_names:

        added_characters = [item["diffs"][differ_name]["added_characters"] for item in data]
        removed_characters = [item["diffs"][differ_name]["removed_characters"] for item in data]
        sizes = [item["size"] for item in data]

        plt.figure(figsize=(25, 5), dpi=250)
        plt.subplots_adjust(bottom=0.15, top=0.95, left=0.02, right=0.99)
        plt.margins(x=0)
        plt.bar(np.arange(len(added_characters)) - 0.15, added_characters, width=0.3, label="added characters")
        plt.bar(np.arange(len(removed_characters)) + 0.15, removed_characters, width=0.3, label="removed characters")
        plt.plot(list(range(len(sizes))), sizes, label="section size", color="green")
        plt.xticks(list(range(len(ticks))), ticks, rotation = 90)
        plt.title("Length of Sections " + "/".join(sections) + " in " + articletitle)
        plt.legend()
        plt.savefig(filepath + "_history_section_analysis_" + differ_name + ".png")    
    
if __name__ == "__main__":

    filepath = "../articles/TEST/Zinc_finger_nuclease_en"

    FINAL_YEAR, FINAL_MONTH = 2021, 2
    sections = {"history":["History",
                           "Discovery and properties",
                           "Discovery of CRISPR"],
                "application":["The significance for evolution and possible applications",
                               "Possible applications",
                               "Applications"]
                }

    differs = {"difflib_differ":difflib_differ(),"custom_differ":custom_differ()}

    section_name = "history"

    data = calculate_data(filepath, "", sections, differs)
    plot_diffs(data, filepath)
    dump(data, open(filepath + "_diff_data.json", "w"))
    timesliced_data = timeslice_data(data, FINAL_YEAR, FINAL_MONTH)
    sizes, reference_counts = plot_size_and_reference_count(timesliced_data, filepath)
