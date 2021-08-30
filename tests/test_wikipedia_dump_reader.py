from code.article.revision.timestamp import Timestamp
from code.bibliography.bibliography import Bibliography
from code.timeline.eventlist import EventList
from code.timeline.accountlist import AccountList
from code.utility.wikipedia_dump_reader import WikipediaDumpReader
import unittest

class TestWikipediaDumpReader(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        bibliography = Bibliography("tests/data/literature.bib")
        accountlist = AccountList("tests/data/accounts.csv")
        cls.eventlist = EventList("tests/data/events.csv",
                                  bibliography,
                                  accountlist,
                                  [],
                                  ["bibentries"])
        
    def test_print(self):

        wdr = WikipediaDumpReader("tests/dumps/enwiki-20210601-pages-meta-history18.xml-p27121491p27121850.bz2")
        doi_count = 0
        pmid_count = 0
        revisions = []
        for revision in wdr:
            for event in self.eventlist.events:
                bibkey = list(event.bibentries.keys())[0]
                doi = event.dois[bibkey]
                pmid = event.pmids[bibkey]
                if revision["text"]:
                    if doi and (doi in revision["text"]):
                        doi_count += 1
                    if pmid and (pmid in revision["text"]):
                        pmid_count += 1
                    if doi and (doi in revision["text"]) \
                       and pmid and (pmid in revision["text"]):
                        revisions.append(revision)
        
        self.assertEqual(doi_count, 17)
        self.assertEqual(pmid_count, 17)

        self.assertEqual(len(revisions), 17)

        self.assertEqual(revisions[0]["revid"], "358506933")
        
        self.assertEqual(revisions[-1]["revid"], "1014921611")

if __name__ == "__main__":
    unittest.main()

