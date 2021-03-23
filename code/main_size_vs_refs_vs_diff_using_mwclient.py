import matplotlib.pyplot as plt
from article.article import Article
from article.revision.timestamp import Timestamp
from differ.lcs import Differ as custom_differ
from difflib import Differ as difflib_differ
from datetime import datetime
from json import load, dump
from os.path import basename, dirname, exists, sep
from glob import glob
from urllib.parse import quote, unquote
from math import sqrt
import numpy as np
from mwclient import Site
from lxml import html

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

def generate_annual_timeslice_ticks(timeslices):
    timeslice_ticks = []
    for timeslice in timeslices:
        year = timeslice.split("/")[-1]
        timeslice_ticks.append(year if year not in timeslice_ticks else "")
    return timeslice_ticks

def generate_articlename(filepath):
    return unquote(basename(filepath).split("_en")[0]).replace("_", " ")

def calculate_data(filepath, strings, title):

    def format_timestamp(timestamp):
        return f"{timestamp.tm_year}-{str(timestamp.tm_mon).rjust(2,'0')}-{str(timestamp.tm_mday).rjust(2,'0')}T{str(timestamp.tm_hour).rjust(2,'0')}:{str(timestamp.tm_min).rjust(2,'0')}:{str(timestamp.tm_sec).rjust(2,'0')}Z"

    def format_url(revision):
        return f"https://en.wikipedia.org/w/index.php?title={title}&oldid={revision['revid']}"

    def added_and_removed(diff):
        h = html.fromstring(diff)
        added = 0
        removed = 0
        for element in h.iter():
            if element.tag == "ins":
                added += len(element.xpath("string()"))
            if element.tag == "del":
                removed += len(element.xpath("string()"))
        return added, removed

    log_file = open(dirname(filepath) + sep + "CALCULATION.log", "a")

    articletitle = generate_articlename(filepath)

    log_file.write("Calculating diffs for " + title + " and sections '" + "', '".join(strings) + "'" + "\n")
    
    site = Site('en.wikipedia.org')
    article = site.pages[title]
    revisions = article.revisions(dir="newer",endid=1008705943,slots="main",prop="ids|content|size|timestamp")
    prev_revision = next(revisions)

    data = [{"revision_timestamp":format_timestamp(prev_revision["timestamp"]),
             "revision_url":format_url(prev_revision),
             "revision_index":0,
             "revision_revid":prev_revision["revid"],
             "size":prev_revision["size"],
             "refcount":0,
             "diffs":{
                 "mwdiff":{
                     "added_characters":prev_revision["size"],
                     "removed_characters":0,
                     "diff":"-"}
                 }
             }
            ]

    start = datetime.now()

    for index,revision in enumerate(revisions, 1):

        log_file.write(str(index) + " " + f"https://en.wikipedia.org/w/index.php?title={title}&oldid={revision['revid']}" + "\n")
        print(index)

        compare_result = site.get('compare', fromrev=prev_revision["revid"], torev=revision["revid"])
        diff = compare_result['compare']['*']
        added_characters, removed_characters = added_and_removed(diff)
        
        data.append(
            {"revision_timestamp":format_timestamp(revision["timestamp"]),
             "revision_url":format_url(prev_revision),
             "revision_index":index,
             "revision_revid":revision["revid"],
             "size":revision["size"],
             "refcount":0,
             "diffs":{
                 "mwdiff":{
                     "added_characters":added_characters,
                     "removed_characters":removed_characters,
                     "diff":"-"}
                 }
             }
            )

        prev_revision = revision

    log_file.write("TOTAL TIME: " + str(datetime.now() - start))

    log_file.close()

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
    reference_counts_label = "References in Section " + section_name + " in " + articletitle

    sizes_color = "b"
    sizes_label = "Size of Section " + section_name + " in " + articletitle

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

    return sizes, reference_counts

def plot_diffs(data, filepath, section_name, width, height):
    articletitle = generate_articlename(filepath)

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
        plt.title("Development of " + section_name + " Section in " + articletitle)
        plt.legend()
        plt.savefig(filepath + "_section_analysis_" + differ_name + ".png")    
    
if __name__ == "__main__":

    filepath = "../analysis/sections/TEST/CRISPR_gene_editing_en"

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

    section_name = "All"
    strings,level = sections[section_name]
    width = 50
    height = 20

    section_filepath = filepath + "_" + section_name.lower()

    if not exists(section_filepath + "_diff_data.json"):
        data = calculate_data(filepath, strings, "CRISPR gene editing")
        dump(data, open(section_filepath + "_diff_data.json", "w"))
    else:
        data = load(open(section_filepath + "_diff_data.json"))
    
    plot_diffs(data, section_filepath, section_name, width, height)
    timesliced_data = timeslice_data(data, 2021, 2)
    plot_size_and_reference_count(timesliced_data, section_filepath)
