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
        cls.output_filepath = "tests/data/wikipedia_dump.parquet"
        cls.csv_filepath = "tests/data/wikipedia_dump.csv"

    @classmethod
    def tearDownClass(cls):
        remove(cls.output_filepath)
        remove(cls.csv_filepath)

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

    def test_parquet_writer(self):
        
        with WikipediaDumpReader(self.input_filepath) as wdr:
            wdr.write_revisions_to_parquet(self.output_filepath)

        self.assertEqual(self.file_checksum(self.output_filepath),
                         "6f062be57af3adba97456d0f212cf27961ca9983aa01c46e259ab353384aed7d")

    def test_csv_analysis(self):
        events = {"bibkey":[],"doi":[],"pmid":[]}
    
        for event in self.eventlist.events:
            bibkey = list(event.bibentries.keys())[0]
            events["bibkey"].append(bibkey)
            events["doi"].append(event.dois[bibkey])
            events["pmid"].append(event.pmids[bibkey])

        events_dataframe = pa.Table.from_pydict(events).to_pandas()

        with WikipediaDumpReader(self.input_filepath) as wdr:
            wdr.write_revisions_to_parquet(self.output_filepath)

        revisions_dataframe = pq.read_table(self.output_filepath).to_pandas()

        with open(self.csv_filepath, "w", newline="") as csvfile:
            csv_writer = csv.writer(csvfile, delimiter=",")
            for revision_index,title,revid,timestamp,text in revisions_dataframe.itertuples():
                for event_index,bibkey,doi,pmid in events_dataframe.itertuples():
                    if text and ((doi and doi in text) or (pmid and pmid in text)):
                        csv_writer.writerow([bibkey,
                                             doi,
                                             pmid,
                                             title,
                                             revid,
                                             Timestamp(timestamp).string])

        self.assertEqual(self.file_checksum(self.csv_filepath),
                        "55672f2b90708ab7b59d452597f9e8706af481c7b4a7e9f80837c13675e3eec3")

if __name__ == "__main__":
    unittest.main()

