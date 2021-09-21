from article.revision.timestamp import Timestamp
from bibliography.bibliography import Bibliography
from timeline.eventlist import EventList
from timeline.accountlist import AccountList
from utility.wikipedia_dump_reader import WikipediaDumpReader
import csv
import logging
import re

from datetime import datetime
from os.path import basename, exists, sep
from glob import glob
from multiprocessing import Pool

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

def process(input_filepath, output_directory, publication_map, doi_and_pmid_regex, done_input_filepaths):
    if basename(input_filepath) in done_input_filepaths:
        with open(output_directory + sep + "done_update.txt", "a") as update_file:
            update_file.write("Analysis of file " + basename(input_filepath) + " already complete.\n")
        return
    output_file_prefix = output_directory + sep + basename(input_filepath).split(".bz2")[0]
    csv_filepath = output_file_prefix + "_results.csv"
    log_filepath = output_file_prefix + "_log.txt"
    start_publication_count = 0
    start_revision_count = 0
    if exists(log_filepath):
        with open(log_filepath) as file:
            last_log_line = file.readlines()[-1]
            try:
                start_publication_count = int(last_log_line.split(",")[0].strip().split(" >>> ")[-1])
                start_revision_count  = int(last_log_line.split(",")[-1].strip())
            except ValueError:
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
        with WikipediaDumpReader(input_filepath) as wdr:
            for title,revid,timestamp,text in wdr.line_iter():
                revision_count += 1
                if start_revision_count and revision_count <= start_revision_count:
                    continue
                if revision_count % 1000 == 0:
                    logger.info(str(publication_count) + "," + str(revision_count))
                for match in set(re.findall(doi_and_pmid_regex, text)):
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

if __name__ == "__main__":

##    corpus_path_prefix = ("../dumps/")
##    input_files = [#"enwiki-20210601-pages-meta-history18.xml-p27121491p27121850.bz2", # 472KB
##                   #"enwiki-20210601-pages-meta-history27.xml-p67791779p67827548.bz2", # 25MB
##                   #"enwiki-20210601-pages-meta-history21.xml-p39974744p39996245.bz2",   # 150MB
##                   "enwiki-20210601-pages-meta-history12.xml-p9089624p9172788.bz2", # 860MB, false positive results
##                   #"enwiki-20210601-pages-meta-history1.xml-p4291p4820.bz2",    # 2GB
##                   ]
##    input_filepaths = [corpus_path_prefix + input_file for input_file in input_files]

    with open("../analysis/dump/done.csv") as file:
        done_input_filepaths = [line.split(",")[0] for line in file.readlines()]

    input_filepaths = sorted(glob("../../../../../corpora/corpora-thirdparty/corpus-wikipedia/wikimedia-history-snapshots/enwiki-20210620/*.bz2"))

    publication_map = {}

    for publication_event in read_and_unify_publication_eventlists():
        bibkey = list(publication_event.bibentries.keys())[0]
        doi = publication_event.dois[bibkey]
        pmid = publication_event.pmids[bibkey]
        wos = publication_event.trace["wos"]
        accounts = publication_event.trace["accounts"]
        if doi: publication_map[doi] = (bibkey, wos, accounts)
        if pmid: publication_map[pmid] = (bibkey, wos, accounts)

    dois_and_pmids = list(publication_map.keys())

    escaped_dois_and_pmids = [re.escape(item) for item in dois_and_pmids]

    doi_and_pmid_regex = re.compile("|".join(escaped_dois_and_pmids))

    output_directory = "../analysis/dump"

    with Pool() as pool:

        pool.starmap(process, [(input_filepath,
                                output_directory,
                                publication_map,
                                doi_and_pmid_regex,
                                done_input_filepaths)
                               for input_filepath in input_filepaths])

