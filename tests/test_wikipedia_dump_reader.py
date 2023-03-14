from code.article.revision.timestamp import Timestamp
from code.bibliography.bibliography import Bibliography
from code.timeline.eventlist import EventList
from code.timeline.accountlist import AccountList
from code.wikidump.wikipedia_dump_reader import WikipediaDumpReader
from hashlib import sha256
from os import remove
import unittest
import csv

class TestWikipediaDumpReader(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.input_directory = "tests/data/wikipedia_dump_reader/"
        bibliography = Bibliography(cls.input_directory + "literature.csv")
        accountlist = AccountList(cls.input_directory + "accounts.csv")
        cls.eventlist = EventList(cls.input_directory + "events.csv",
                                  bibliography,
                                  accountlist,
                                  [],
                                  ["bibentries"])
        cls.input_filepath1 = cls.input_directory + "wikipedia_dump_1.bz2"
        cls.input_filepath2 = cls.input_directory + "wikipedia_dump_2.bz2"
    
    def test_iterator_1(self):

        doi_count = 0
        pmid_count = 0
        revisions = []
        with WikipediaDumpReader(self.input_filepath1) as wdr:
            for title, pageid, revid, timestamp, text in wdr.line_iter():
                for event in self.eventlist.events:
                    bibkey = list(event.bibentries.keys())[0]
                    doi = event.dois[bibkey]
                    pmid = event.pmids[bibkey]
                    if text:
                        if doi and (doi in text):
                            doi_count += 1
                        if pmid and (pmid in text):
                            pmid_count += 1
                        if doi and (doi in text) \
                           and pmid and (pmid in text):
                            revisions.append((title, pageid, revid, timestamp, text))
        
        self.assertEqual(doi_count, 17)
        self.assertEqual(pmid_count, 17)

        self.assertEqual(len(revisions), 17)

        self.assertEqual(revisions[0][1], "27121514")

        self.assertEqual(revisions[0][2], "358506933")
        
        self.assertEqual(revisions[-1][2], "1014921611")

    def test_iterator_2(self):

        titles = []
        pageids = []
        revids = []
        texts = []

        with WikipediaDumpReader(self.input_filepath2) as wdr:
            for title, pageid, revid, timestamp, text in wdr.line_iter():
                if title not in titles:
                    titles.append(title)
                if pageid not in pageids:
                    pageids.append(pageid)
                if revid not in revids:
                    revids.append(revid)
                texts.append(text)

        self.maxDiff = None
        self.assertEqual(len(titles), 2)
        self.assertEqual(titles[0], "1.6 Band")
        self.assertEqual(titles[1], "Derek Panza")
        self.assertEqual(len(pageids), 2)
        self.assertEqual(pageids[0], "27121496")
        self.assertEqual(pageids[1], "27121502")
        self.assertEqual(len(revids), 193 - 11)
        self.assertEqual(revids[0], "358506549")
        self.assertEqual(revids[-1], "918238989")
        self.assertEqual(len(texts), 193 - 11)

        with open(self.input_directory + "first_text.txt") as file:
            self.assertEqual(texts[0], "".join(file.readlines()))
        with open(self.input_directory + "final_text.txt") as file:
            self.assertEqual(texts[-1], "".join(file.readlines()))

    def test_text_reading(self):

        titles = []
        pageids = []
        revids = []
        texts = []
        
        with WikipediaDumpReader(self.input_filepath1) as wdr:
            for title, pageid, revid, timestamp, text in wdr.line_iter():
                if title not in titles:
                    titles.append(title)
                if pageid not in pageids:
                    pageids.append(pageid)
                if revid not in revids:
                    revids.append(revid)
                texts.append(text)
        
        self.maxDiff = None
        self.assertEqual(titles[0], "1.6 Band")
        self.assertEqual(pageids[0], "27121496")
        self.assertEqual(revids[0], "358506549")
        with open(self.input_directory + "first_text.txt") as file:
            self.assertEqual(texts[0], "".join(file.readlines()))

if __name__ == "__main__":
    unittest.main()

