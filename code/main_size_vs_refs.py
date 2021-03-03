import matplotlib.pyplot as plt
from article.article import Article
from datetime import datetime
from json import load, dump
from os.path import basename, exists
from glob import glob
from urllib.parse import quote, unquote
from math import sqrt

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

filepaths = glob("../articles/TEST/*_en")
SAVE = False
TIMESLICING = True
FINAL_YEAR, FINAL_MONTH = 2021, 2

for filepath in filepaths:

    articletitle = "'" + unquote(basename(filepath)).replace("_", " ")[:-3] + "'"

    if not exists(filepath + "_revision_size_vs_reference_length.json"):

        print("Calculating " + articletitle)
        
        article = Article(filepath)

        first_timestamp = article.get_revision(0).timestamp
        FIRST_YEAR, FIRST_MONTH = first_timestamp.year, first_timestamp.month

        if TIMESLICING:
            timeslices = []
            timeslice_ticks = []
            for year in range(FIRST_YEAR, FINAL_YEAR + 1):
                for month in range(1, 13):
                    if (year > FIRST_YEAR or month >= FIRST_MONTH) and \
                       (year < FINAL_YEAR or month <= FINAL_MONTH):
                        timeslices.append(str(month) + "/" + str(year))
                        timeslice_ticks.append(str(year) if str(year) not in timeslice_ticks else "")
            data = {timeslice:{"size":[],"refcount":[]} for timeslice in timeslices}

            for revision in article.yield_revisions():
                timeslice = str(revision.timestamp.month) + "/" + str(revision.timestamp.year)
                
                if revision.index % 100 == 0: print(revision.index)
                if timeslice in data:
                    data[timeslice]["size"].append(revision.size)
                    data[timeslice]["refcount"].append(len(revision.get_references() + revision.get_further_reading()))

            prev_size = 0
            prev_refcount = 0

            for timeslice in data:
                try:
                    data[timeslice]["size"] = sum(data[timeslice]["size"])/len(data[timeslice]["size"])
                    prev_size = data[timeslice]["size"]
                except ZeroDivisionError:
                    data[timeslice]["size"] = prev_size
                try:
                    data[timeslice]["refcount"] = sum(data[timeslice]["refcount"])/len(data[timeslice]["refcount"])
                    prev_refcount = data[timeslice]["refcount"]
                except ZeroDivisionError:
                    data[timeslice]["refcount"] = prev_refcount

            sizes = [timeslice["size"] for timeslice in data.values()]
            reference_counts = [timeslice["refcount"] for timeslice in data.values()]
        else:
            sizes = []
            reference_counts = []
            for revision in article.yield_revisions():
                if revision.index % 100 == 0: print(revision.index)
                sizes.append(revision.size)
                reference_counts.append(len(revision.get_references() + revision.get_further_reading()))
            timeslice_ticks = range(len(sizes))
                           
        if SAVE:
            dump({"timeslice_ticks":timeslice_ticks,
                  "sizes":sizes,
                  "reference_counts":reference_counts},
                 open(filepath + "_revision_size_vs_reference_length.json", "w"))
    else:
        data = load(open(filepath + "_revision_size_vs_reference_length.json"))
        timeslice_ticks = data["timeslice_ticks"]
        sizes = data["sizes"]
        reference_counts = data["reference_counts"]

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
    
    print()
