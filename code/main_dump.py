from article.revision.timestamp import Timestamp
from bibliography.bibliography import Bibliography
from timeline.eventlist import EventList
from timeline.accountlist import AccountList
from multiprocessing import Pool
from xml.etree import ElementTree
import bz2
import csv
import logging

from datetime import datetime
from os.path import basename
from re import findall
from glob import glob

class WikipediaDumpReader(object):

    def __init__(self, filepath):
        self.filepath = filepath
        self.bz2_file = bz2.open(self.filepath, "rb")
        self.xml_iterator = ElementTree.iterparse(self.bz2_file)
        self.namespaces = self._get_namespaces()

    def __enter__(self):
        """Makes the API autoclosable."""
        return self

    def __exit__(self, type, value, traceback):
        """Close XML file handle."""
        self.bz2_file.close()

    def _get_namespaces(self):
        namespaces = findall(r'\{.+?\}', next(self.xml_iterator)[1].tag)
        return {"":"http://www.mediawiki.org/xml/export-0.10/",
                "ns0":"http://www.mediawiki.org/xml/export-0.10/",
                "xsi":"http://www.w3.org/2001/XMLSchema-instance"}

    def __iter__(self):
        read_revisions = False
        for event, element in self.xml_iterator:
            if element.tag.endswith("title"):
                revision_result = {"title":element.text} 
            if element.tag.endswith("ns"):
                read_revisions = element.text == "0"
            if element.tag.endswith("revision") and read_revisions:
                for subelement in element:
                    if subelement.tag.endswith("id"):
                        revision_result["revid"] = subelement.text
                    if subelement.tag.endswith("timestamp"):
                        revision_result["timestamp"] = Timestamp(subelement.text).string
                    if subelement.tag.endswith("text"):
                        revision_result["text"] = subelement.text
                yield revision_result
                element.clear()
            if not read_revisions: element.clear()

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

def process(filenpath, publication_events):
    start = datetime.now()
    revision_count = 0
    publication_count = 0
    fileprefix = "../analysis/dump/" + basename(filenpath).split(".")[0]
    with open(fileprefix + "_results.csv", "w", newline="") as csvfile:
        logger, logging_file_handler = get_logger(fileprefix + "_log.txt")
        csv_writer = csv.writer(csvfile, delimiter=",")
        with WikipediaDumpReader(filenpath) as dr:
            for revision_result in dr:
                for publication_event in publication_events:
                    bibkey = list(publication_event.bibentries.keys())[0]
                    doi = publication_event.dois[bibkey]
                    pmid = publication_event.pmids[bibkey]
                    if revision_result["text"] \
                       and ((doi and doi in revision_result["text"]) \
                            or (pmid and pmid in revision_result["text"])):
                        publication_count += 1
                        eventlist = "|".join([key for key,value in publication_event.trace.items() if value])
                        csv_writer.writerow([bibkey,
                                             doi,
                                             pmid,
                                             revision_result["title"],
                                             revision_result["revid"],
                                             revision_result["timestamp"],
                                             eventlist])
                revision_count += 1
                if revision_count % 1000 == 0:
                    logger.info(str(revision_count) + "," + str(publication_count))
        logger.info(str(revision_count) + "," + str(publication_count))
        end = datetime.now()
        duration = end - start
        logger.info(duration)
        logging_file_handler.close()
        logger.removeHandler(logging_file_handler)
        with open("../analysis/dump/done.csv", "a", newline="") as done_file:
            done_file_writer = csv.writer(done_file, delimiter=",")
            done_file_writer.writerow([basename(filenpath), revision_count, publication_count, duration])

if __name__ == "__main__":

    corpus_path_prefix = ("../../../../../corpora/corpora-thirdparty/corpus-wikipedia/" +
                          "wikimedia-history-snapshots/enwiki-20210620/")

    filenpaths = [corpus_path_prefix + file for file in
                  ["enwiki-20210601-pages-meta-history18.xml-p27121491p27121850.bz2", # 472KB
                   "enwiki-20210601-pages-meta-history27.xml-p67791779p67827548.bz2", # 25MB
                  #"enwiki-20210601-pages-meta-history13.xml-p10996375p11055008.bz2", # 1GB
                  #"enwiki-20210601-pages-meta-history8.xml-p2607466p2641559.bz2",    # 2GB
                  #"enwiki-20210601-pages-meta-history14.xml-p13148370p13184925.bz2", # 3GB
                  #"enwiki-20210601-pages-meta-history9.xml-p3706897p3741659.bz2")    # 5GB
                  #"enwiki-20210601-pages-meta-history8.xml-p2535881p2535914.bz2")    # 7GB
                   ]
                  ]

    filepaths = sorted(glob(corpus_path_prefix + "*.bz2"))
    print(len(filepaths), " BZ2 files.")
    
    bibliography = Bibliography("../data/tracing-innovations-lit.bib")
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

    print("Sanity check successful.")
                
    with Pool(20) as pool:
        pool.starmap(process, [(filenpath, publication_events) for filenpath in filenpaths])

