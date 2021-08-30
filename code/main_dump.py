from article.revision.timestamp import Timestamp
from bibliography.bibliography import Bibliography
from timeline.eventlist import EventList
from timeline.accountlist import AccountList
from utility.wikipedia_dump_reader import WikipediaDumpReader
import csv
import logging

from datetime import datetime
from os.path import basename, sep
from glob import glob
from pprint import pprint
import pyarrow.parquet as pq
import pyarrow as pa

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
    publication_events = []
    
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

    return publication_events

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

def process(revisions_dataframe, publications_dataframe, output_directory):
    start = datetime.now()
    revision_count = 0
    publication_count = 0
    output_file_prefix = output_directory + sep + basename(input_filepath).split(".bz2")[0]
    with open(output_file_prefix + "_results.csv", "w", newline="") as csvfile:
        logger, logging_file_handler = get_logger(output_file_prefix + "_log.txt")
        csv_writer = csv.writer(csvfile, delimiter=",")
        for revision_index,title,revid,timestamp,text in revisions_dataframe.itertuples():
            revision_count = revision_index + 1
            if revision_count % 1000 == 0:
                logger.info(str(revision_count) + "," + str(publication_count))
            for publication_index,bibkey,doi,pmid,wos,accounts in publications_dataframe.itertuples():
                if text and ((doi and doi in text) or (pmid and pmid in text)):
                    publication_count += 1
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

        logger.info(str(revision_count) + "," + str(publication_count))
        end = datetime.now()
        duration = end - start
        logger.info(duration)
        logging_file_handler.close()
        logger.removeHandler(logging_file_handler)
        with open("../analysis/dump/done.csv", "a", newline="") as done_file:
            done_file_writer = csv.writer(done_file, delimiter=",")
            done_file_writer.writerow([basename(input_filepath),
                                       revision_count,
                                       publication_count,
                                       duration])

if __name__ == "__main__":

    corpus_path_prefix = ("/media/wolfgang/Ceph/corpora/corpora-thirdparty/corpus-wikipedia/" +
                          "wikimedia-history-snapshots/enwiki-20210620/")

    input_files = ["enwiki-20210601-pages-meta-history18.xml-p27121491p27121850.bz2", # 472KB
                   #"enwiki-20210601-pages-meta-history27.xml-p67791779p67827548.bz2", # 25MB
                   #"enwiki-20210601-pages-meta-history12.xml-p9089624p9172788.bz2",   # 1GB
                   #"enwiki-20210601-pages-meta-history8.xml-p2607466p2641559.bz2",    # 2GB
                   #"enwiki-20210601-pages-meta-history14.xml-p13148370p13184925.bz2", # 3GB
                   #"enwiki-20210601-pages-meta-history9.xml-p3706897p3741659.bz2")    # 5GB
                   #"enwiki-20210601-pages-meta-history8.xml-p2535881p2535914.bz2")    # 7GB
                   ]
    
    input_filepath = corpus_path_prefix + input_files[0]

    output_directory = "../analysis/dump"

    output_filepath = output_directory + sep + basename(input_filepath).split(".bz2")[0] + "_revisions.parquet"

    #input_filepaths = sorted(glob(corpus_path_prefix + "*.bz2"))
    print(len(input_files), "BZ2 file(s).")

    try:
        publication_dataframe = pq.read_table(output_directory + sep + "publications.parquet").to_pandas()
    except FileNotFoundError:
        publication_events = read_and_unify_publication_eventlists()
        write_publication_events_to_parquet(publication_events, output_directory + sep + "publications.parquet")
        publication_dataframe = pq.read_table(output_directory + sep + "publications.parquet").to_pandas()

    try:
        revisions_dataframe = pq.read_table(output_filepath).to_pandas()
    except FileNotFoundError:
        with WikipediaDumpReader(input_filepath) as wdr:
            wdr.write_revisions_to_parquet(output_filepath)
        revisions_dataframe = pq.read_table(output_filepath).to_pandas()    
                
    process(revisions_dataframe, publication_dataframe, output_directory)

