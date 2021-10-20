from code.article.revision.timestamp import Timestamp
from code.bibliography.bibliography import Bibliography
from code.timeline.eventlist import EventList
from code.timeline.accountlist import AccountList
from code.utility.wikipedia_dump_reader import WikipediaDumpReader
import pyarrow.parquet as pq
import pyarrow as pa
from hashlib import sha256
from os import remove
import unittest
import csv

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
        cls.input_filepath = "tests/data/wikipedia_dump.bz2"

    def file_checksum(self, filepath):
        sha256_hash = sha256()
        with open(filepath,"rb") as f:
            for byte_block in iter(lambda: f.read(4096),b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    
    def test_iterator(self):

        doi_count = 0
        pmid_count = 0
        revisions = []
        with WikipediaDumpReader(self.input_filepath) as wdr:
            for title, revid, timestamp, text in wdr.line_iter():
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
                            revisions.append((title, revid, timestamp, text))
        
        self.assertEqual(doi_count, 17)
        self.assertEqual(pmid_count, 17)

        self.assertEqual(len(revisions), 17)

        self.assertEqual(revisions[0][1], "358506933")
        
        self.assertEqual(revisions[-1][1], "1014921611")

if __name__ == "__main__":
    unittest.main()

