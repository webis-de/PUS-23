from article.article import Article
from article.revision.timestamp import Timestamp
from bibliography.bibliography import Bibliography
from timeline.eventlist import EventList
from timeline.accountlist import AccountList
from utility.wikipedia_dump_reader import WikipediaDumpReader
import csv
import logging
import regex as re

from datetime import datetime
from os.path import basename, exists, sep
from os import makedirs
from glob import glob
from multiprocessing import Pool
import matplotlib.pyplot as plt
from time import sleep

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

def read_and_increment_index_counter():
    if not exists("index.txt"):
        index = 0
    else:
        with open("index.txt") as file:
            index = int(file.readline().strip())
    with open("index.txt", "w") as file:
        file.write(str(index + 1))
    return index

def get_dates():
    dates = []
    for year in range(2001,2022):
        for month in range(1, 13):
            dates.append(str(month).rjust(2, "0") + "/" + str(year))
    return dates

def process(input_filepath,
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
                #for match in re.finditer(doi_and_pmid_regex, text):
                for match in sorted(set([item.group() for item in re.finditer(doi_and_pmid_regex, text)])):
                    if match:
                        #match = match.group().replace("pmid = ", "")
                        match = match.replace("pmid = ", "")
                        publication_count += 1
                        bibkey, wos, accounts = publication_map[match]
                        eventlist = "|".join([key for key,value
                                              in [("wos",wos),
                                                  ("accounts",accounts)] if value])
                        csv_writer.writerow([bibkey,
                                             match,
                                             title,
                                             revid,
                                             Timestamp(timestamp).string,
                                             eventlist])
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

if __name__ == "__main__":

    test = False
    multi = False
    quick = False

##    with open("../data/CRISPR_articles.txt") as article_titles_file:
##        article_titles = [article_title.strip() for article_title in article_titles_file.readlines()]
##
##    if test:
##        corpus_path_prefix = ("../dumps/")
##        input_files = [#"enwiki-20210601-pages-meta-history18.xml-p27121491p27121850.bz2", # 472KB
##                       #"enwiki-20210601-pages-meta-history27.xml-p67791779p67827548.bz2", # 25MB
##                       #"enwiki-20210601-pages-meta-history21.xml-p39974744p39996245.bz2",   # 150MB
##                       #"enwiki-20210601-pages-meta-history12.xml-p9089624p9172788.bz2", # 860MB, false positive results
##                       #"enwiki-20210601-pages-meta-history1.xml-p10133p11053.bz2",    # 2GB
##                       "enwiki-20210601-pages-meta-history11.xml-p6324364p6396854.bz2" # broken results CSV
##                       ]
##        input_filepaths = [corpus_path_prefix + input_file for input_file in input_files]
##    else:
##        corpus_path_prefix = "../../../../../" + \
##                             "corpora/corpora-thirdparty/corpus-wikipedia/wikimedia-history-snapshots/enwiki-20210620/"
##        input_filepaths = glob(corpus_path_prefix + "*.bz2")
##
##    output_directory = "../analysis/dump_test"
##    if not exists(output_directory): makedirs(output_directory)
##    
##    done_filepath = output_directory + sep + "done.csv"
##    if exists(done_filepath):
##        with open(done_filepath) as file:
##            done_input_filepaths = [line.split(",")[0] for line in file.readlines()]
##    else:
##        done_input_filepaths = []

    publication_map = {}
    dois = []
    pmids = []
    bibkeys = []
    unified_publication_events = read_and_unify_publication_eventlists()
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
    
    doi_and_pmid_regex = re.compile("|".join(dois) + "|" + "(pmid = (" + ("|".join(pmids)) + "))")

    article_filenames = sorted(glob("../articles/2021-10-04_wikitext_only/en/*_en"))

    print(article_filenames)

    dates = get_dates()[:-7]

    results = {date:{} for date in dates}

    for index,article_filename in enumerate(article_filenames, 1):
        article = Article(article_filename)
        for date in dates:
            results[date][article.name] = {bibkey:False for bibkey in bibkeys}

    fig, ax = plt.subplots()
    fig.set_dpi(100.0)
    fig.set_figheight(80)
    fig.set_figwidth(50)
    with open("results.csv", "w") as csvfile:
        for article_filename in article_filenames:
            article = Article(article_filename)
            print(article.name)
            revisions = article.yield_revisions()
            date_revision_map = {date:False for date in dates}
            for revision in revisions:
                month = str(revision.timestamp.month).rjust(2, "0")
                year = str(revision.timestamp.year)
                date = month + "/" + year
                date_revision_map[date] = True

                #print(revision.index, revision.url)

                for match in sorted(set([item.group().replace("pmid = ", "") for item in re.finditer(doi_and_pmid_regex, revision.get_wikitext())])):
                    bibkey, wos, accounts = publication_map[match]
                    results[date][article.name][bibkey] = 1 if wos else 2

            for i in range(1, len(dates)):
                if not date_revision_map[dates[i]] and date_revision_map[dates[i-1]]:
                    results[dates[i]] = results[dates[i-1]]
                    date_revision_map[dates[i]] = True

            csv_writer = csv.writer(csvfile, delimiter=",")
            line = []
            for date in dates:
                wos_count = 0
                acc_count = 0
                for bibkey in results[date][article.name]:
                    if results[date][article.name][bibkey] == 1:
                        wos_count += 1
                    if results[date][article.name][bibkey] == 2:
                        acc_count += 1
                line.append(str(wos_count) + "/" + str(wos_count + acc_count))
            csv_writer.writerow([article.name] + line)

            data = {'x': dates,
                    'y': [article.name for y in dates],
                    'c': [((len([value for value in results[date][article.name].values() if value in [1]])/
                            len([value for value in results[date][article.name].values() if value in [1,2]]))
                           if len([value for value in results[date][article.name].values() if value in [1,2]]) > 0 else 0)
                          for date in dates],
                    'd': [len([value for value in results[date][article.name].values() if value in [1,2]]) for date in dates]}
        
            ax.scatter('x', 'y', c='c', s='d', data=data, cmap='Greys')
                
        csv_writer = csv.writer(csvfile, delimiter=",")
        csv_writer.writerow([""] + dates)
        
        ax.set(xlabel='Months', ylabel='Name of Article')
        ax.tick_params(axis='x', labelrotation=90)
        ax.margins(x=0.005, y=0.005)
        plt.subplots_adjust(left=0.09, right=0.9975, bottom=0.0125, top=0.999)
        plt.savefig("results.png")
        plt.savefig("results.jpg")

##    if multi:
##        with Pool(3) as pool:
##
##            pool.starmap(process, [(input_filepath,
##                                    output_directory,
##                                    publication_map,
##                                    doi_and_pmid_regex,
##                                    done_input_filepaths,
##                                    article_titles,
##                                    quick)
##                                   for input_filepath in input_filepaths])
##    else:
##        for input_filepath in input_filepaths:
##            process(input_filepath,
##                    output_directory,
##                    publication_map,
##                    doi_and_pmid_regex,
##                    done_input_filepaths,
##                    article_titles,
##                    quick)
