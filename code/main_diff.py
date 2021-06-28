import matplotlib.pyplot as plt
from article.article import Article
from article.revision.timestamp import Timestamp
from differ.differ import Differ as custom_differ
from difflib import Differ as difflib_differ
from datetime import datetime
from json import load, loads, dump, dumps
from os.path import basename, dirname, exists, sep
from os import makedirs
from glob import glob
from urllib.parse import quote, unquote
from math import sqrt
from preprocessor.preprocessor import Preprocessor
import numpy as np
import logging

#################################################################
# This file serves as an entry point to diff Wikipedia articles.#
#################################################################

def get_logger(directory):
    """Set up the logger."""
    logger = logging.getLogger("diff_logger")
    formatter = logging.Formatter("%(asctime)s >>> %(message)s", "%F %H:%M:%S")
    logger.setLevel(logging.DEBUG)
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    stream_handler.setLevel(logging.INFO)
    file_handler = logging.FileHandler(directory + sep + "log.txt", "a")
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.DEBUG)
    logger.addHandler(stream_handler)
    logger.addHandler(file_handler)
    return logger

def corr_coef(X,Y):
    """
    Calculate Pearsons Correlation Coefficient.
    Args:
        X: The first list of data.
        Y: The second list of data.
    Returns:
        Pearsons Correlation Coefficient of X and Y.
    """
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
    """
    Collate data by MONTH/YEAR timestamp.
    Args:
        data: A list of data entries with associated timestamps
              under the key 'revision_timestamp'.
        FINAL_YEAR: Last year to consider.
        FINAL_MONTH: Last month to consider.
    Returns:
        A new data set with entries grouped as per their month and year.
    """
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
    """
    Convert timeslice ticks by adding leading zeros (months == True)
    or cleaning the months and keeping only the first year (months == False):
        - if months: '7/2010 -> 07/2010'
        - if not months: '7/2010 -> 2010'
    Args:
        months: Flag for retaining months.
    Returns:
        List of timestamp strings.
    """
    timeslice_ticks = []
    for timeslice in timeslices:
        year = timeslice.rjust(7, "0") if months else timeslice.split("/")[-1]
        timeslice_ticks.append(year if year not in timeslice_ticks else "")
    return timeslice_ticks

def calculate_data(filepath, logger, section_strings, section_level, differs, preprocessor = None, problematic_revids = []):
    """
    Analyses all revisions, generating diffs for the section as defined by the section strings provided and
    provides a data map containing revision metadata, revision size, reference counts and diffs for each revision.

    If no section strings are provided, i.e. an empty list, the entire revision is used as basis.

    Args:
        filepath: Path to the revision file.
        logger: The logger this method uses.
        section_strings: List of strings defining the sections to use.
        section_level: Depth to which the section will be explored.
        differs: The differ objects to apply.
        preprocessor: Preprocessor used to handle tokenization.
        problematic_revids: Revids to skip.
    """
    article = Article(filepath)

    logger.info("Calculating diffs for " + article.name + " and sections '" + "', '".join(section_strings) + "'")

    data = []

    prev_text = ""

    start = datetime.now()

    for revision in article.yield_revisions():

        logger.info(str(revision.index + 1) + " " + str(revision.url))

        if revision.revid in problematic_revids:
            logger.info("Blacklisted revid: " + str(revision.revid))
            continue

        if section_strings != []:
            section_tree = revision.section_tree()
            section = section_tree.find(section_strings, True)
            text = section[0].get_text(section_level, include = ["p","li"], with_headings=True) if section else ""
            if preprocessor:
                text = preprocessor.preprocess(text, lower=False, stopping=False, sentenize=False, tokenize=True)[0]
            references = section[0].get_sources(revision.get_references(), section_level) if section else []
        else:
            text = revision.get_text()
            references = revision.get_references() + revision.get_further_reading()

        diffs = {differ_name:list(differ.compare(prev_text, text))
                 for differ_name, differ in differs.items()}
        
        data.append(
            {"revision_timestamp":revision.timestamp.timestamp_string(),
             "revision_url":revision.url,
             "revision_index":revision.index,
             "revision_revid":revision.revid,
             "size":sum([len(item) for item in text]) if section_strings != [] else revision.size,
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

    logger.info("TOTAL TIME: " + str(datetime.now() - start))

    return data

def save_data(data, section_filepath):
    with open(section_filepath + "_diff_data.json", "w") as data_file:
        for line in data:
            data_file.write(dumps(line) + "\n")

def load_data(data_filepath):
    with open(data_filepath) as file:
        return [loads(line) for line in file]

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

def handle_timesliced_data(timesliced_data):
    sizes = []
    reference_counts = []
    added_characters = []
    removed_characters = []
    timeslice_ticks = [item if item[:2] in ["01","04","07","10"] else "" for index,item in enumerate(generate_annual_timeslice_ticks(timesliced_data, True))]

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

    reference_counts_color = "k"
    reference_counts_label = "Number of References in " + article_name + " Article"

    sizes_color = "k"
    sizes_label = "Size of " + article_name + " Article in Characters"

    fig, ax1 = plt.subplots(figsize=(12,6), dpi=500)
    plt.xticks(list(range(len(timeslice_ticks))), timeslice_ticks, rotation=90)
    ax1.plot(list(range(len(reference_counts))), reference_counts, label=reference_counts_label, color=reference_counts_color, linestyle=":")
    ax1.set_ylabel(reference_counts_label, color=reference_counts_color, fontsize="xx-large")
    ax1.tick_params('y', colors=reference_counts_color)
    ax1.margins(x=0.005)
    ax2 = ax1.twinx()
    ax2.plot(list(range(len(sizes))), sizes, label=sizes_label, color=sizes_color)
    ax2.set_ylabel(sizes_label, color=sizes_color, fontsize="xx-large")
    ax2.tick_params('y', colors=sizes_color)
    ax1.set_ylim(ymin=0)
    ax2.set_ylim(ymin=0)
    ax2.margins(x=0.005)
    #plt.subplots_adjust(bottom=0.12, top=0.98, left=0.12, right=0.88)
    #plt.title("PCC: " + str(pcc))
    fig.legend(loc="upper left", bbox_to_anchor=(0.1, 0.93), fontsize="xx-large")
    fig.tight_layout()
    plt.savefig(filepath + "_section_revision_size_vs_reference_length.pdf", transparent=True)
    plt.close('all')

def plot_size_and_reference_count_and_diffs(timesliced_datasets, analysis_directory, logger, section_name, differ_name):

    fig = plt.figure(figsize=(30,6), dpi=300)
    axs = [plt.subplot2grid((12, 48), (0, 0), colspan=41, rowspan=12),
           plt.subplot2grid((12, 48), (0, 41), colspan=6, rowspan=12)]

    first_plot = True
    reference_max = None
    sizes_max = None

    article_abbreviation_index = 1

    for timesliced_data, ax1 in zip(timesliced_datasets, axs):
        
        sizes, reference_counts, added_characters, removed_characters, timeslice_ticks = handle_timesliced_data(timesliced_datasets[timesliced_data])

        if first_plot:
            reference_max = max(reference_counts)
            sizes_max = max(max(added_characters),max(removed_characters),max(sizes))

        try:
            pcc = round(corr_coef(sizes, reference_counts), 3)
        except:
            pcc = "n/a"

        logger.info("Plotting " + timesliced_data + " " + section_name)
        logger.info("PCC: " + str(pcc))
        
        if not first_plot:
            fig.legend(bbox_to_anchor=(0.2075, 0.9), prop={'size': 15})
        
        #x ticks
        ax1.set_xticks(list(range(len(timeslice_ticks))))
        ax1.set_xticklabels(timeslice_ticks, rotation=90)

        #sizes
        ax1.margins(x=0.005)
        ax1.plot(list(range(len(sizes))), sizes, label="Mean Character Count", color="k", linewidth=1.5)
        if first_plot:
            ax1.set_ylabel("Characters", color="k", fontsize="xx-large")
        else:
            ax1.set_yticks([])
            ax1.set_yticklabels([])
        ax1.set_ylim(ymin=0, ymax=sizes_max)
        
        #reference counts
        ax2 = ax1.twinx()
        ax2.margins(x=0.005)
        ax2.plot(list(range(len(reference_counts))), reference_counts, label="Mean Number of References", color="k", linestyle=":", linewidth=1.5)
        if not first_plot:
            ax2.set_ylabel("References", color="k", fontsize="xx-large")
        else:
            ax2.set_yticks([])
            ax2.set_yticklabels([])
        ax2.set_ylim(ymin=0, ymax=reference_max)

        #added characters
        ax1.bar(np.arange(len(added_characters)) - 0.25, added_characters, width=0.5, label="Total Number of Added Characters", color="lightgray")
        #removed characters
        ax1.bar(np.arange(len(removed_characters)) + 0.25, removed_characters, width=0.5, label="Total Number of Removed Characters", color="darkgray")

        plt.title("\"" + timesliced_data + "\" (C" + str(article_abbreviation_index) + ")", fontsize="xx-large")
        article_abbreviation_index += 1

        first_plot = False
        plt.legend([" PCC References to \nCharacters = " + str(pcc).ljust(5,"0")], frameon=False, handlelength=0.0, loc="upper center", fontsize="x-large")

    plt.subplots_adjust(bottom=0.2, top=0.925, left=0.04, right=0.9925)
    
    plt.savefig(analysis_directory + sep + "_".join(timesliced_datasets.keys()).replace(" ","_") + "_" + section_name  + "_" + "section_revision_size_vs_references_vs_diffs.png")
    plt.close('all')
    
if __name__ == "__main__":

    import matplotlib

    matplotlib.rc('xtick', labelsize=15) 
    matplotlib.rc('ytick', labelsize=15)

    problematic_revids = load(open("../data/problematic_revids.json"))
    problematic_revids_CRISPR_en = [item[0] for item in problematic_revids["CRISPR_en"]]
    problematic_revids_CRISPR_gene_editing_en = [item[0] for item in problematic_revids["CRISPR_gene_editing_en"]]

    language = "en"

    preprocessor = Preprocessor(language)

    articles = (
##        ("CRISPR",16.5,True,problematic_revids_CRISPR_en),
##        ("CRISPR_gene_editing",3.5,False,problematic_revids_CRISPR_gene_editing_en),
        ("Cas9",16.5,True,[]),
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
                                10),
                "NO_SECTION_TREE":([],0)
                }

    differs = {"custom_differ":custom_differ()}#"difflib_differ":difflib_differ(),"custom_differ":custom_differ()}

    articles_directory = "../articles/2021-02-14"
    analysis_directory = "../analysis/sections/2021_06_28" + sep + str(datetime.now())[:-7].replace(":","_").replace("-","_").replace(" ","_")

    if not exists(analysis_directory): makedirs(analysis_directory)
    
    logger = get_logger(analysis_directory)

    for section_name in ["All","Intro","History","Application"]:

        timesliced_datasets = {}
        
        for article_name,width,legend,problematic_revids in articles:

            differ_name = "custom_differ"
            section_strings,section_level = sections[section_name]
            height = 6
            
            articles_filepath = articles_directory + sep + article_name + "_" + language
            analysis_filepath = analysis_directory + sep + article_name + "_" + language + "_" + section_name.lower()

            if not exists(analysis_filepath + "_diff_data.json"):
                data = calculate_data(articles_filepath, logger, section_strings, section_level, differs, preprocessor, problematic_revids)
                save_data(data, analysis_filepath)
            else:
                data = load_data(analysis_filepath + "_diff_data.json")

            timesliced_datasets[article_name.replace("_", " ")] = timeslice_data(data, 2020, 12)

            #plot_size_and_reference_count(timeslice_data(data, 2021, 2), analysis_filepath, article_name, section_name) #different result compared to previous version due to use of section tree!
            
        plot_size_and_reference_count_and_diffs(timesliced_datasets, analysis_directory, logger, section_name, differ_name)
