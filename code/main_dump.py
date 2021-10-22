##from article.article import Article
##from bibliography.bibliography import Bibliography
##from timeline.eventlist import EventList
##from timeline.accountlist import AccountList
from article.revision.timestamp import Timestamp
from utility.wikipedia_dump_reader import WikipediaDumpReader
import csv
import logging
import regex as re

from datetime import datetime
from os.path import basename, exists, getsize, sep
from os import environ
from os import makedirs
from glob import glob
from socket import gethostname

##import matplotlib.pyplot as plt
##import matplotlib.colors as mcol

def get_logger(filename):
    """Set up the logger."""
    logger = logging.getLogger("dump_logger")
    formatter = logging.Formatter("%(asctime)s >>> %(message)s", "%F %H:%M:%S")
    logger.setLevel(logging.DEBUG)
    logging_file_handler = logging.FileHandler(filename, "a")
    logging_file_handler.setFormatter(formatter)
    logging_file_handler.setLevel(logging.DEBUG)
    logger.addHandler(logging_file_handler)
    return logger, logging_file_handler

def read_and_unify_publication_eventlists():
    start = datetime.now()
    publication_events = set()

    bibliography = Bibliography("../data/CRISPR_literature.bib")
    accountlist = AccountList("../data/CRISPR_accounts.csv")
    publication_events_accounts = set(EventList("../data/CRISPR_publication-events.csv",
                                                bibliography,
                                                accountlist,
                                                [],
                                                ["bibentries"]).events)
    publication_events_wos = set(EventList("../data/CRISPR_publication-events-hochzitierte.csv",
                                           bibliography,
                                           accountlist,
                                           [],
                                           ["bibentries"]).events)

    for publication_event in publication_events_accounts.union(publication_events_wos):
        publication_event.trace["wos"] = (publication_event in publication_events_wos)
        publication_event.trace["accounts"] = (publication_event in publication_events_accounts)
        publication_events.add(publication_event)

    print(len(publication_events), "publication event(s).", datetime.now() - start)

    return publication_events

def read_and_unify_publication_eventlists_for_tests():
    bibliography = Bibliography("../tests/data/literature.bib")
    accountlist = AccountList("../tests/data/accounts.csv")
    eventlist = EventList("../tests/data/events.csv",
                           bibliography,
                           accountlist,
                           [],
                           ["bibentries"])
    eventlist.events[0].trace = {"wos":True, "accounts":False}
    return eventlist.events

def log_handler_host(output_directory, hostname, nodename, input_filepath_index, input_filepath, filesize):
    with open(output_directory + sep + hostname + ".txt", "a") as file:
        file.write(str(input_filepath_index).rjust(3, "0") + " " + basename(input_filepath) + " " + nodename + " " + str(filesize / (1024**2)) + "\n")    

def get_timeslices(first_year = 2001, final_year = 2021):
    timeslices = []
    for year in range(first_year,final_year + 1):
        for month in range(1, 13):
            timeslices.append(str(month).rjust(2, "0") + "/" + str(year))
    return timeslices

def get_publication_data_bib(test = False):
    publication_map = {}
    dois = []
    pmids = []
    bibkeys = []
    unified_publication_events = eval("read_and_unify_publication_eventlists" + ("_for_tests" if test else "") + "()")
    for publication_event in unified_publication_events:
        bibkey = list(publication_event.bibentries.keys())[0]
        bibkeys.append(bibkey)
        doi = publication_event.dois[bibkey]
        pmid = publication_event.pmids[bibkey]
        wos = publication_event.trace["wos"]
        accounts = publication_event.trace["accounts"]
        if doi:
            dois.append(re.escape(doi))
            publication_map[doi] = (bibkey, wos, accounts)
        if pmid:
            pmids.append(re.escape(pmid))
            publication_map[pmid] = (bibkey, wos, accounts)
    return (publication_map, dois, pmids, bibkeys)

def get_publication_data_csv():
    dois = set()
    pmids = set()
    with open("../data/CRISPR_literature.csv") as csvfile:
        csv_reader = csv.reader(csvfile, delimiter="|")
        header = True
        for wos_uid, title, doi, pmid in csv_reader:
            if header:
                header = False
                continue
            if doi: dois.add(doi)
            if pmid: pmids.add(pmid)
    return (dois, pmids)                

def analyse_dump(input_filepath,
                 output_directory,
                 publication_map,
                 doi_and_pmid_regex,
                 done_input_filepaths,
                 article_titles,
                 quick = False):
    output_file_prefix = output_directory + sep + basename(input_filepath).split(".bz2")[0]
    csv_filepath = output_file_prefix + "_results.csv"
    log_filepath = output_file_prefix + "_log.txt"
    if basename(input_filepath) in done_input_filepaths:
        with open(output_directory + sep + "done_update.txt", "a") as update_file:
            update_file.write("Analysis of file " + basename(input_filepath) + " already complete.\n")
        return
    start_publication_count = 0
    start_revision_count = 0
    if exists(log_filepath):
        return
        with open(log_filepath) as file:
            try:
                last_log_line = file.readlines()[-1]
                try:
                    start_publication_count = int(last_log_line.split(",")[0].strip().split(" >>> ")[-1])
                    start_revision_count  = int(last_log_line.split(",")[-1].strip())
                except ValueError:
                    pass
            except IndexError:
                pass

        with open(output_directory + sep + "done_update.txt", "a") as update_file:
            update_file.write("Analysis of file " + basename(input_filepath) + " already started. " + \
                              "Starting from " + str(start_publication_count) + " publications and " + \
                              str(start_revision_count) + " revisions.\n")
    with open(csv_filepath, "a", newline="") as csvfile:
        start = datetime.now()
        revision_count = 0
        publication_count = max([0, start_publication_count])
        logger, logging_file_handler = get_logger(log_filepath)
        csv_writer = csv.writer(csvfile, delimiter=",")
        old_title = None
        skip = False
        with WikipediaDumpReader(input_filepath, article_titles) as wdr:
            for title,revid,timestamp,text in wdr.line_iter():
                revision_count += 1
                if start_revision_count and revision_count <= start_revision_count:
                    continue
                if revision_count % 1000 == 0:
                    logger.info(str(publication_count) + "," + str(revision_count))
                if quick:
                    if title != old_title:
                        skip = False
                    if title == old_title and skip:
                        continue
                matches = re.finditer(doi_and_pmid_regex, text)
                for match in sorted(set([item.group() for item in re.finditer(doi_and_pmid_regex, text)])):
                    if match:
                        publication_count += 1
                        #bibkey, wos, accounts = publication_map[match]
                        #eventlist = "|".join([key for key,value
                        #                      in [("wos",wos),
                        #                          ("accounts",accounts)] if value])
                        csv_writer.writerow([#bibkey,
                                             match,
                                             title,
                                             revid,
                                             Timestamp(timestamp).string
                                             #eventlist
                                             ])
                        csvfile.flush()
                        if quick:
                            skip = True
                            break
                old_title = title
        logger.info(str(publication_count) + "," + str(revision_count))
        end = datetime.now()
        duration = end - start
        logger.info(duration)
        logging_file_handler.close()
        logger.removeHandler(logging_file_handler)
        with open(output_directory + sep + "done.csv", "a", newline="") as done_file:
            done_file_writer = csv.writer(done_file, delimiter=",")
            done_file_writer.writerow([basename(input_filepath),
                                       publication_count,
                                       revision_count,
                                       duration])
            done_file.flush()

def analyse_article(article_filepath, timeslices, publication_map, bibkeys):
    article = Article(article_filepath)
    article_name = article.name

    results = {timeslice:{bibkey:False for bibkey in bibkeys} for timeslice in timeslices}
                
    revisions = article.yield_revisions()
    timeslice_revision_map = {timeslice:False for timeslice in timeslices}
    for revision in revisions:
        month = str(revision.timestamp.month).rjust(2, "0")
        year = str(revision.timestamp.year)
        timeslice = month + "/" + year
        timeslice_revision_map[timeslice] = True

        for match in sorted(set([item.group().replace("pmid = ", "") for item in re.finditer(doi_and_pmid_regex, revision.get_wikitext())])):
            bibkey, wos, accounts = publication_map[match]
            results[timeslice][bibkey] = "wos" if wos else "any"

    for i in range(1, len(timeslices)):
        if not timeslice_revision_map[timeslices[i]] and timeslice_revision_map[timeslices[i-1]]:
            results[timeslices[i]] = results[timeslices[i-1]]
            timeslice_revision_map[timeslices[i]] = True

    line = []
    for timeslice in timeslices:
        wos_count = 0
        any_count = 0
        for bibkey in results[timeslice]:
            if results[timeslice][bibkey] == "wos":
                wos_count += 1
            if results[timeslice][bibkey] == "any":
                any_count += 1
        line.append(str(wos_count) + "/" + str(wos_count + any_count))
    print(article_name)
    return [article_name] + line

if __name__ == "__main__":

    test_files = [#"enwiki-20210601-pages-meta-history18.xml-p27121491p27121850.bz2", # 472KB
                  #"enwiki-20210601-pages-meta-history27.xml-p67791779p67827548.bz2", # 25MB
                  #"enwiki-20210601-pages-meta-history21.xml-p39974744p39996245.bz2",   # 150MB
                  #"enwiki-20210601-pages-meta-history12.xml-p9089624p9172788.bz2", # 860MB, false positive results
                  #"enwiki-20210601-pages-meta-history1.xml-p10133p11053.bz2",    # 2GB
                  #"enwiki-20210601-pages-meta-history11.xml-p6324364p6396854.bz2" # broken results CSV
                  "enwiki-20210601-pages-meta-history10.xml-p5128920p5137511.bz2"] # 55 GB

    positive_files = ["enwiki-20210601-pages-meta-history16.xml-p19095128p19200231.bz2",
                      "enwiki-20210601-pages-meta-history25.xml-p59825024p60146730.bz2",
                      "enwiki-20210601-pages-meta-history1.xml-p11828p12504.bz2",
                      "enwiki-20210601-pages-meta-history21.xml-p38516211p38695815.bz2",
                      "enwiki-20210601-pages-meta-history1.xml-p12505p13384.bz2"]

    pattern = ['"((10\.)(" + "|".join([doi[3:] for doi in dois]) + "))" + "|" + ' + \
               '"(([pP][mM][iI][dD][ =:]{0,5})(" + ("|".join(pmids)) + "))"',
               '"(10\.)" + "(" + "|".join([doi[3:] for doi in dois]) + ")"',
               '"|".join(dois) + "|" + "(([pP][mM][iI][dD][ =:]{0,5})(" + ("|".join(pmids)) + "))"',
               '"|".join(dois) + "|" + "((pmid = |PMID )(" + ("|".join(pmids)) + "))"',
               '"|".join(dois) + "|" + "(pmid = (" + ("|".join(pmids)) + "))"',
               '"|".join(dois)) + "|" + ("|".join(pmids)'
               ][0]

    test = False
    quick = True
    slice_size = 1

    JOB_COMPLETION_INDEX = 0#int(environ.get("JOB_COMPLETION_INDEX"))

    output_directory = "../analysis/articles/articles_candidates_from_dump_new_big_file"
    if not exists(output_directory): makedirs(output_directory)

    done_filepath = output_directory + sep + "done.csv"
    if exists(done_filepath):
        with open(done_filepath) as file:
            done_input_filepaths = [line.split(",")[0] for line in file.readlines()]
    else:
        done_input_filepaths = []

    if test:
        corpus_path_prefix = ("../dumps/")
        corpus_path_prefix = "../../../../../" + \
                             "corpora/corpora-thirdparty/corpus-wikipedia/wikimedia-history-snapshots/enwiki-20210601/"
        input_filepaths = [corpus_path_prefix + input_file for input_file in test_files]
    else:
        corpus_path_prefix = "../../../../../" + \
                             "corpora/corpora-thirdparty/corpus-wikipedia/wikimedia-history-snapshots/enwiki-20210601/"
        input_filepaths = sorted(glob(corpus_path_prefix + "*.bz2"))
        input_filepaths.remove(corpus_path_prefix + "enwiki-20210601-pages-meta-history10.xml-p5128920p5137511.bz2")
        input_filepaths = [corpus_path_prefix + "enwiki-20210601-pages-meta-history10.xml-p5128920p5137511.bz2"]

    #publication_map, dois, pmids, bibkeys = get_publication_data_bib(False)
    dois, pmids = get_publication_data_csv()

    doi_and_pmid_regex = re.compile(eval(pattern))

    for input_filepath_index, input_filepath in enumerate(input_filepaths[JOB_COMPLETION_INDEX*slice_size:(JOB_COMPLETION_INDEX+1)*slice_size], JOB_COMPLETION_INDEX*slice_size):
        filesize = getsize(input_filepath)
        hostname = gethostname()
        log_handler_host(output_directory, hostname, "" if True else environ.get("NODE_NAME"), input_filepath_index, input_filepath, filesize)
        
        analyse_dump(input_filepath=input_filepath,
                     output_directory=output_directory,
                     publication_map={},
                     doi_and_pmid_regex=doi_and_pmid_regex,
                     done_input_filepaths=done_input_filepaths,
                     article_titles=[],
                     quick=quick)

##    article_filepaths = sorted(glob("../articles/2021-06-01_wikitext_only/en/*_en"))
##    relevant_article_filepath = [("../data/CRISPR_articles.txt", "_all"),
##                                 ("../data/CRISPR_articles_relevant.txt","_relevant"),
##                                 ("../data/CRISPR_articles_relevant_no_persons.txt","_relevant_no_persons")
##                                 ][0]
##
##    with open(relevant_article_filepath[0]) as file:
##        relevant_article_names = set([line.strip() for line in file.readlines()])
##        
##    timeslices = get_timeslices(2001)[:-7]
##
##    csv_data_filepath = "../analysis/bibliography/2021_10_06/dump_analysis_plot_data.csv"
##    if not exists(csv_data_filepath):
##        publication_map, dois, pmids, bibkeys = get_publication_data_bib()
##        doi_and_pmid_regex = re.compile(eval(pattern))
##        
##        with open(csv_data_filepath, "w") as csvfile:
##            csv_writer = csv.writer(csvfile, delimiter=",")
##            with Pool() as pool:
##                lines = [line for line in pool.starmap(analyse_article, [(article_filepath, timeslices, publication_map, bibkeys)
##                                                                         for article_filepath in article_filepaths])]
##
##            for line in lines:
##                csv_writer.writerow(line)
##            csv_writer.writerow([""] + timeslices)
##    else:
##        lines = []
##        with open(csv_data_filepath) as csvfile:
##            csv_reader = csv.reader(csvfile, delimiter=",")
##            for row in csv_reader:
##                if row[0] in relevant_article_names:
##                    lines.append(row)
##                    
##    bibkey_max_per_month_count_sort_map = {line[0]:max([int(item.split("/")[-1]) for item in line[1:]])
##                                           for line in lines}
##
##    lines = sorted(lines, key=lambda line: bibkey_max_per_month_count_sort_map[line[0]])
##    
##    start_index = 1
##    for i in range(1, len(lines[0])):
##        if any([line[i] != "0/0" for line in lines]):
##            start_index = i
##            break
##    start_index -= 1
##
##    timeslices = timeslices[start_index-1:]
##    lines = [[line[0]] + line[start_index:] for line in lines]
##       
##    cm = mcol.LinearSegmentedColormap.from_list("MyCmapName",["b","r"])    
##    fig, ax = plt.subplots()
##    fig.set_dpi(1000.0)
##    height = int(len(lines)/5)*1.5
##    width = len(timeslices[start_index:])/10
##    fig.set_figheight(height)
##    fig.set_figwidth(width)          
##        
##    for line in lines:
##        #ax.plot(timeslices, [line[0] for _ in timeslices], linewidth=0.3, color="gray", zorder=0)
##        data = {'x': timeslices,
##                'y': [line[0] for _ in timeslices],
##                'c': [eval(item) if item != "0/0" else 0.0 for item in line[1:]],
##                'd': [float(item.split("/")[-1])*3 for item in line[1:]]}
##        
##        ax.scatter('x', 'y', c='c', s='d', data=data, cmap=cm, zorder=1, marker=[(0, 3),(0,-3)], linewidth=3)
##        
##    ax.set(xlabel='', ylabel='')
##    ax.tick_params(axis='x', labelsize=6.0, labelrotation=90)
##    ax.tick_params(axis='y', labelsize=10.0)
##    ax.set_xticklabels([timeslice if index % 6 == 0 else "" for index,timeslice in enumerate(timeslices)])
##    ax.margins(x=0.005, y=0.3/height)
##    
##    adjustment_left = 3.75/width
##    adjustment_right = 0.995
##    adjustment_bottom = 0.5/height
##    adjustment_top = 0.995
##    
##    plt.subplots_adjust(left=adjustment_left,
##                        right=adjustment_right,
##                        bottom=adjustment_bottom,
##                        top=adjustment_top)
##
##    print("articles:", relevant_article_filepath[1].replace("_", " ").strip())
##    print("height:", height, "width:", width)
##    print("\n\t".join(["adjustments:",
##                     "left: " + str(adjustment_left),
##                     "right: " + str(adjustment_right),
##                     "bottom: " + str(adjustment_bottom),
##                     "top: " + str(adjustment_top)]))
##    
##    plt.savefig(output_directory + sep + "plot" + relevant_article_filepath[1] + ".png")
            

