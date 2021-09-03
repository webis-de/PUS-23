from article.revision.timestamp import Timestamp
from bibliography.bibliography import Bibliography
from timeline.eventlist import EventList
from timeline.accountlist import AccountList
from utility.wikipedia_dump_reader import WikipediaDumpReader
import csv
import logging
import re

from datetime import datetime
from os.path import basename, sep
from glob import glob
from multiprocessing import Pool

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

def write_publication_events_to_parquet(publication_events, output_filepath):

    publications = {"bibkey":[],"doi":[],"pmid":[],"wos":[],"accounts":[]}
    
    for publication_event in publication_events:
        bibkey = list(publication_event.bibentries.keys())[0]
        publications["bibkey"].append(bibkey)
        publications["doi"].append(publication_event.dois[bibkey])
        publications["pmid"].append(publication_event.pmids[bibkey])
        publications["wos"].append(publication_event.trace["wos"])
        publications["accounts"].append(publication_event.trace["accounts"])

    table = pa.Table.from_pydict(publications)
    pq.write_table(table, output_filepath)

def process(input_filepath, output_directory, publication_map_dois, publication_map_pmids, doi_and_pmid_regex):
    output_file_prefix = output_directory + sep + basename(input_filepath).split(".bz2")[0]
    with open(output_file_prefix + "_results.csv", "w", newline="") as csvfile:
        start = datetime.now()
        revision_count = 0
        publication_count = 0
        logger, logging_file_handler = get_logger(output_file_prefix + "_log.txt")
        csv_writer = csv.writer(csvfile, delimiter=",")
        with WikipediaDumpReader(input_filepath) as wdr:
            for title,revid,timestamp,text in wdr.line_iter():
                revision_count += 1
                if revision_count % 1000 == 0:
                    logger.info(str(publication_count) + "," + str(revision_count))
                for result in re.findall(doi_and_pmid_regex, text):
                    publication_count += 1
                    try:
                        bibkey, doi, wos, accounts = publication_map_pmids[result]
                        pmid = result
                    except KeyError:
                        bibkey, pmid, wos, accounts = publication_map_dois[result]
                        doi = result
                    
                    eventlist = "|".join([key for key,value
                                          in [("wos",wos),
                                              ("accounts",accounts)] if value])
                    csv_writer.writerow([bibkey,
                                         doi,
                                         pmid,
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

    input_filepaths = glob("../../../../../corpora/corpora-thirdparty/corpus-wikipedia/wikimedia-history-snapshots/enwiki-20210620/*.bz2")

    publication_map_dois = {}
    publication_map_pmids = {}

    for publication_event in read_and_unify_publication_eventlists():
        bibkey = list(publication_event.bibentries.keys())[0]
        doi = publication_event.dois[bibkey]
        pmid = publication_event.pmids[bibkey]
        wos = publication_event.trace["wos"]
        accounts = publication_event.trace["accounts"]
        if doi: publication_map_dois[doi] = (bibkey, pmid, wos, accounts)
        if pmid: publication_map_pmids[pmid] = (bibkey, doi, wos, accounts)

    dois_and_pmids = list(publication_map_dois.keys()) + list(publication_map_pmids.keys())

    escaped_dois_and_pmids = [re.escape(item) for item in dois_and_pmids]

    doi_and_pmid_regex = re.compile("|".join(escaped_dois_and_pmids))

    output_directory = "../analysis/dump"

    with Pool() as pool:
        
        pool.starmap(process, [(input_filepath, output_directory, publication_map_dois, publication_map_pmids, doi_and_pmid_regex)
                               for input_filepath in input_filepaths])

