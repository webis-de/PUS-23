from wikidump.wikitext_reader import WikitextReader
from wikidump.wikipedia_dump_reader import WikipediaDumpReader
from json import load
from pprint import pprint
from datetime import datetime
from regex import search
from csv import writer
from numpy import mean, std

analyse = True
verbose = False
doi_map = {}

with open("../analysis/citations/citations_from_wikitext_test.csv", "w") as citation_file:
    with open("../analysis/citations/latency_from_wikitext_test.csv", "w") as latency_file:
        citation_csv_writer = writer(citation_file, delimiter="|")
        latency_csv_writer = writer(latency_file, delimiter="|")
        citation_csv_writer.writerow(["title", "title_year", "revision_index", "revid", "doi", "reference_year", "revision_year", "citation_latency"])
        latency_csv_writer.writerow(["title", "pageid", "number of dois", "mean citation latency", "standard deviation"])
        with WikipediaDumpReader(("/media/wolfgang/Data/Work/git/code-research/computational-social-science/" +
                                  "science-analytics-wikipedia/dumps/enwiki-20230301-pages-meta-history10.xml-p5382015p5399366.bz2")) as wdr:
            old_title = None
            revision_index = 0
            title_year = None
            latencies = []
            for title,pageid,revid,timestamp,text in wdr.line_iter():
                if title not in doi_map:
                    doi_map[title] = set()
                if title != old_title:
                    if len(latencies) >= 10:
                        latency_csv_writer.writerow([title, pageid, len(latencies), round(mean(latencies), 2), round(std(latencies), 2)])
                        latency_file.flush()
                        latencies = []
                    old_title = title
                    title_year = None
                    revision_index = 0
                if analyse:
                    doi_found = False
                    wtr = WikitextReader(title,pageid,revid,timestamp,text)
                    if verbose: print(title, revid, timestamp)
                    revision_year = datetime.strptime(wtr.timestamp, "%Y-%m-%dT%H:%M:%SZ").year
                    if not title_year:
                        title_year = revision_year
                    for reference in wtr.references():
                        doi = reference.get("doi", None)
                        if doi:
                            doi_found = True
                            if verbose: print("-"*50)
                            if verbose: pprint(reference, sort_dicts=False)
                            if reference.get("year", None) and len(reference["year"]) == 4:
                                reference_year = int(reference["year"])
                            elif reference.get("date", None):
                                match = search("\d\d\d\d", reference["date"])
                                if match and len(match.group()) == 4:
                                    reference_year = int(match.group())
                            else:
                                reference_year = None
                            if doi not in doi_map[title]:
                                doi_map[title].add(doi)
                                if title_year and revision_year and reference_year:
                                    citation_latency = revision_year - max([reference_year, title_year])
                                    latencies.append(citation_latency)
                                    citation_csv_writer.writerow([title, title_year,
                                                                  revision_index, revid,
                                                                  doi, reference_year, revision_year, citation_latency])
                                    citation_file.flush()
                            if verbose: print(reference["title"])
                            if verbose: print("\tReference year:", reference_year)
                            if verbose: print("\tRevision year:", revision_year)
                         
                    if verbose: print("="*50)
                    if doi_found:
                        if verbose: input()
                        doi_found = False

                revision_index += 1   
