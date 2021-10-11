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

    def test_parquet_writer(self):
        
        with WikipediaDumpReader(self.input_filepath) as wdr:
            wdr.write_revisions_to_parquet(self.output_filepath)

        self.assertEqual(self.file_checksum(self.output_filepath),
                         "96b5ae404d60224c0916b0319475e8c1710ab0bff8c461050cccc7633b33ef85")

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

