from wikidump.wikitext_reader import WikitextReader
from json import load
from pprint import pprint
from datetime import datetime
from regex import search

with open("/mnt/Data/uni/09THESIS/ba-kircheis-wikipedia-code/corpora/2022_03_29_01_39_26/science_and_technology_corpus.json") as file:
    corpus = load(file)

for entry in corpus:
    wtr = WikitextReader(entry["article_title"],
                         entry["pageid"],
                         entry["revid"],
                         entry["timestamp"],
                         entry["wikitext"])
    revision_year = datetime.strptime(wtr.timestamp, "%Y-%m-%dT%H:%M:%SZ").year
    for reference in wtr.references():
        if reference.get("doi", None):
            pprint(reference)
            if reference.get("year", None) and len(reference["year"]) == 4:
                reference_year = int(reference["year"])
            elif reference.get("date", None):
                match = search("\d\d\d\d", reference["date"])
                if match and len(match.group()) == 4:
                    reference_year = int(match.group())
            else:
                reference_year = None
            print(reference["title"])
            print("\tReference year:", reference_year)
            print("\tRevision year:", revision_year)
            print("-"*50)
    input("="*50)
