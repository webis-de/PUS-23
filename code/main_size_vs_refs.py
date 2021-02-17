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
    Sxx = 1
    Syy = 1
    for i in range (0, len(X)):
        Sxy += (X[i] - mean_x) * (Y[i] - mean_y)
        Sxx += (X[i] - mean_x)**2
        Syy += (Y[i] - mean_y)**2

    return Sxy / sqrt(Sxx * Syy)

filepaths = glob("../articles/2021-02-14/*_en")
save = True

for filepath in filepaths:

    articletitle = unquote(basename(filepath)).replace("_", " ")[:-3]

    if not exists(filepath + "_revision_size_vs_reference_length.json"):

        print("Calculating " + articletitle)
        
        article = Article(filepath)

        first_revision = article.get_revision(0)

        timeslices = []
        for year in range(2000, 2021):
            if year < first_revision.timestamp.year: continue
            for month in range(1, 13):
                if year == first_revision.timestamp.year and month < first_revision.timestamp.month: continue
                timeslices.append(str(month) + "/" + str(year))

        data = {timeslice:{"size":[],"refcount":[]} for timeslice in timeslices}

        last_size = None

        count = 0

        for revision in article.yield_revisions():
            timeslice = str(revision.timestamp.month) + "/" + str(revision.timestamp.year)
            if timeslice not in data:
                continue
            if revision.index % 100 == 0:
                print(revision.index)
            if revision.index != 0 and revision.size == 0:
                continue
            if revision.index != 0 and (revision.size/last_size < 0.2 or revision.size/last_size > 5):
                continue
            else:
                count += 1
                data[timeslice]["size"].append(revision.size)
                data[timeslice]["refcount"].append(len(revision.get_references() + revision.get_further_reading()))
            last_size = revision.size

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
        timeslices = list(data.keys())

        last_timeslice = timeslices[0].split("/")[-1]
        new_timeslices = [timeslices[0].split("/")[-1]]
        for timeslice in timeslices[1:]:
            new_timeslice = timeslice.split("/")[-1]
            if new_timeslice == last_timeslice:
                new_timeslices.append("")
            else:
                new_timeslices.append(new_timeslice)
                last_timeslice = new_timeslice
        if save:
            dump({"new_timeslices":new_timeslices,
                  "sizes":sizes,
                  "reference_counts":reference_counts},
                 open(filepath + "_revision_size_vs_reference_length.json", "w"))
    else:
        data = load(open(filepath + "_revision_size_vs_reference_length.json"))
        new_timeslices = data["new_timeslices"]
        sizes = data["sizes"]
        reference_counts = data["reference_counts"]

    try:
        cc = corr_coef(sizes, reference_counts)
    except:
        cc = "ERROR"

    print("Correlation Coefficient:", cc)

    print("Plotting " + articletitle)

    reference_counts_color = "y"
    reference_counts_label = f"References in {articletitle}"

    sizes_color = "b"
    sizes_label = f"Size of {articletitle}"

    fig, ax1 = plt.subplots()
    plt.xticks(list(range(len(new_timeslices))), new_timeslices, rotation=90)
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
    plt.title("Correlation Coefficient: " + str(cc))
    fig.tight_layout()
    plt.savefig(filepath + "_revision_size_vs_reference_length.png")
    plt.close('all')
    
    print()
