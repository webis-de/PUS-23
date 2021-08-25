from article.revision.timestamp import Timestamp
from bibliography.bibliography import Bibliography
from timeline.eventlist import EventList
from timeline.accountlist import AccountList
import bz2
import xml.etree.ElementTree as ET
from re import findall
from datetime import datetime
from multiprocessing import Pool

class DumpReader(object):

    def __init__(self, filepath):
        self.filepath = filepath
        self.xml_file = bz2.open(self.filepath, "r")
        self.xml_iterator = ET.iterparse(self.xml_file)
        self.namespaces = self._get_namespaces()

    def __enter__(self):
        """Makes the API autoclosable."""
        return self

    def __exit__(self, type, value, traceback):
        """Close XML file handle."""
        self.xml_file.close()

    def _get_namespaces(self):
        namespaces = findall(r'\{.+?\}', next(self.xml_iterator)[1].tag)
        return {"":namespaces[0][1:-1]}

    def _find(self, element, key):
        return element.find(key, self.namespaces)

    def _findall(self, element, key):
        return element.findall(key, self.namespaces)

    def __iter__(self):
        for event, element in self.xml_iterator:
            if "page" in element.tag:
                if self._find(element, "ns").text == "0":
                    for revision in self._findall(element, "revision"):
                        yield {"title":self._find(element, "title").text,
                               "revid":self._find(revision, "id").text,
                               "timestamp":Timestamp(self._find(revision, "timestamp").text).string,
                               "text":self._find(revision, "text").text}
                element.clear()

if __name__ == "__main__":

    filename = ("/media/wolfgang/Ceph/corpora/corpora-thirdparty/corpus-wikipedia/" +
                "wikimedia-history-snapshots/enwiki-20210620/" +
                "enwiki-20210601-pages-meta-history27.xml-p67791779p67827548.bz2")
    
    bibliography = Bibliography("../data/tracing-innovations-lit.bib")
    accountlist = AccountList("../data/CRISPR_accounts.csv")
    #publication_events = EventList("../data/CRISPR_publication-events.csv", bibliography, accountlist, [], ["bibentries"])
    publication_events_highly_cited = EventList("../data/CRISPR_publication-events-hochzitierte.csv", bibliography, accountlist, [], ["bibentries"])

##    event1 = None
##    event2 = None
##
##    for event in publication_events.events:
##        if "makarova:2002" in event.bibentries:
##            event1 = event
##            break
##
##    for event in publication_events_highly_cited.events:
##        if "makarova:2002" in event.bibentries:
##            event2 = event
##            break

    for publication_event in publication_events_highly_cited.events:
        publication_event.trace = []
        
    start = datetime.now()
    count = 0
    with DumpReader(filename) as dr:
        for revision in dr:
            for publication_event in publication_events_highly_cited.events:
                bibkey = list(publication_event.bibentries.keys())[0]
                doi = publication_event.dois[bibkey]
                pmid = publication_event.pmids[bibkey]
                if revision["text"] \
                   and ((doi and doi in revision["text"]) \
                        or (pmid and pmid in revision["text"])):
                    publication_event.trace.append(revision)
            count += 1
            if count % 100 == 0:
                print(count)
    print(count)
    end = datetime.now()
    print(end - start)
