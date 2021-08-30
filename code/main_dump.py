from article.revision.timestamp import Timestamp
from bibliography.bibliography import Bibliography
from timeline.eventlist import EventList
from timeline.accountlist import AccountList
from utility.wikipedia_dump_reader import WikipediaDumpReader
from multiprocessing import Pool
import csv
import logging

from datetime import datetime
from os.path import basename, sep
from glob import glob
from pprint import pprint

def get_logger(filename):
    """Set up the logger."""
    logger = logging.getLogger("dump_logger")
    formatter = logging.Formatter("%(asctime)s >>> %(message)s", "%F %H:%M:%S")
    logger.setLevel(logging.DEBUG)
    logging_file_handler = logging.FileHandler(filename, "w")
    logging_file_handler.setFormatter(formatter)
    logging_file_handler.setLevel(logging.DEBUG)
    logger.addHandler(logging_file_handler)
    return logger, logging_file_handler

def process(input_filenpath, output_directory, publication_events):
    start = datetime.now()
    revision_count = 0
    publication_count = 0
    fileprefix = output_directory + sep + basename(input_filenpath).split(".bz2")[0]
    with open(fileprefix + "_results.csv", "w", newline="") as csvfile:
        logger, logging_file_handler = get_logger(fileprefix + "_log.txt")
        csv_writer = csv.writer(csvfile, delimiter=",")
        with WikipediaDumpReader(input_filenpath) as dr:
            for revision in dr:
                revision_count += 1
                if revision_count % 1000 == 0:
                    logger.info(str(revision_count) + "," + str(publication_count))
                for publication_event in publication_events:
                    bibkey = list(publication_event.bibentries.keys())[0]
                    doi = publication_event.dois[bibkey]
                    pmid = publication_event.pmids[bibkey]
                    if revision["text"] \
                       and ((doi and doi in revision["text"]) \
                            or (pmid and pmid in revision["text"])):
                        publication_count += 1
                        eventlist = "|".join([key for key,value in publication_event.trace.items() if value])
                        csv_writer.writerow([bibkey,
                                             doi,
                                             pmid,
                                             revision["title"],
                                             revision["revid"],
                                             Timestamp(revision["timestamp"]).string,
                                             eventlist])
                        csvfile.flush()

        logger.info(str(revision_count) + "," + str(publication_count))
        end = datetime.now()
        duration = end - start
        logger.info(duration)
        logging_file_handler.close()
        logger.removeHandler(logging_file_handler)
        with open("../analysis/dump/done.csv", "a", newline="") as done_file:
            done_file_writer = csv.writer(done_file, delimiter=",")
            done_file_writer.writerow([basename(input_filenpath),
                                       revision_count,
                                       publication_count,
                                       duration])

if __name__ == "__main__":

    corpus_path_prefix = ("/media/wolfgang/Ceph/corpora/corpora-thirdparty/corpus-wikipedia/" +
                          "wikimedia-history-snapshots/enwiki-20210620/")

    input_filepaths = [corpus_path_prefix + file for file in
                  ["enwiki-20210601-pages-meta-history18.xml-p27121491p27121850.bz2", # 472KB
                   #"enwiki-20210601-pages-meta-history27.xml-p67791779p67827548.bz2", # 25MB
                   #"enwiki-20210601-pages-meta-history12.xml-p9089624p9172788.bz2",   # 1GB
                   #"enwiki-20210601-pages-meta-history8.xml-p2607466p2641559.bz2",    # 2GB
                   #"enwiki-20210601-pages-meta-history14.xml-p13148370p13184925.bz2", # 3GB
                   #"enwiki-20210601-pages-meta-history9.xml-p3706897p3741659.bz2")    # 5GB
                   #"enwiki-20210601-pages-meta-history8.xml-p2535881p2535914.bz2")    # 7GB
                   ]
                  ]

    #input_filepaths = sorted(glob(corpus_path_prefix + "*.bz2"))
    print(len(input_filepaths), "BZ2 file(s).")
    
    bibliography = Bibliography("../data/CRISPR_literature.bib")
    accountlist = AccountList("../data/CRISPR_accounts.csv")
    publication_events_accounts = EventList("../data/CRISPR_publication-events.csv",
                                            bibliography,
                                            accountlist,
                                            [],
                                            ["bibentries"]).events
    publication_events_wos = EventList("../data/CRISPR_publication-events-hochzitierte.csv",
                                       bibliography,
                                       accountlist,
                                       [],
                                       ["bibentries"]).events

    publication_events = []

    for publication_event in publication_events_accounts:
        if publication_event not in publication_events:
            publication_event.trace["accounts"] = True
            publication_event.trace["wos"] = False
            publication_events.append(publication_event)

    for publication_event in publication_events_wos:
        if publication_event in publication_events:
            publication_events.remove(publication_event)
            publication_event.trace["wos"] = True
            publication_event.trace["accounts"] = True
            publication_events.append(publication_event)
        else:
            publication_event.trace["wos"] = True
            publication_event.trace["accounts"] = False
            publication_events.append(publication_event)

    for publication_event in publication_events:
        assert(publication_event.trace["wos"] == (publication_event in publication_events_wos))
        assert(publication_event.trace["accounts"] == (publication_event in publication_events_accounts))

    print("Sanity check complete.", len(publication_events), "publication event(s).")
                
    with Pool() as pool:
        pool.starmap(process, [(input_filenpath, "../analysis/dump/", publication_events)
                               for input_filenpath in input_filepaths])

