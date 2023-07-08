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
results = {}

start = datetime.now()

with open("../analysis/citations/citations_from_wikitext_test.csv", "w") as citation_file:
    with open("../analysis/citations/latency_from_wikitext_test.csv", "w") as latency_file:
        citations_csv_writer = writer(citation_file, delimiter="|")
        latencies_csv_writer = writer(latency_file, delimiter="|")
        citations_csv_writer.writerow(["title", "pageid", "title_creation_year", "revid", "doi", "reference_year", "revision_year", "citation_latency"])
        latencies_csv_writer.writerow(["title", "pageid", "title_creation_year", "number of unique dois over revision history", "mean citation latency", "standard deviation"])
        with WikipediaDumpReader(("/mnt/Data/work/git/code-research/computational-social-sience/conf20-science-analytics-wikipedia/dumps/" +
        "enwiki-20220101-pages-meta-history10.xml-p5392815p5399366.bz2")) as wdr: #"enwiki-20210601-pages-meta-history21.xml-p39974744p39996245.bz2
            revision_index = 0
            title_creation_year = None
            for title,pageid,revid,timestamp,wikitext in wdr.line_iter():
                # collect doi hits for title
                if title not in results:
                    results[title] = {"pageid":pageid,
                                      "title_creation_year":None,
                                      "citations":{}
                                      }
                if analyse:
                    # start reading wikitext of entry
                    doi_found = False
                    wtr = WikitextReader(title,pageid,revid,timestamp,wikitext)
                    if verbose: print(title, revid, timestamp)
                    revision_year = datetime.strptime(wtr.timestamp, "%Y-%m-%dT%H:%M:%SZ").year
                    # set title creation year to year of first revision
                    if not results[title]["title_creation_year"]:
                        title_creation_year = revision_year
                        results[title]["title_creation_year"] = title_creation_year
                    # start analysing references if any
                    for reference in wtr.references():
                        doi = reference.get("doi", None)
                        if doi:
                            if verbose:
                                print("-"*50)
                                pprint(reference, sort_dicts=False)
                            if reference.get("year", None) and len(reference["year"]) == 4:
                                reference_year = int(reference["year"])
                            elif reference.get("date", None):
                                match = search("\d\d\d\d", reference["date"])
                                if match and len(match.group()) == 4:
                                    reference_year = int(match.group())
                            else:
                                reference_year = None
                            # new DOI: add doi to list of citations, calculate citation latency, append latency to list of latencies, write citation
                            if doi not in results[title]["citations"]:
                                if title_creation_year and revision_year and reference_year:
                                    citation_latency = revision_year - max([reference_year, title_creation_year])
                                    results[title]["citations"][doi] = [title, pageid, title_creation_year, revid, doi, reference_year, revision_year, citation_latency]
                                    
                            if verbose:
                                print(reference["title"])
                                print("\tReference year:", reference_year)
                                print("\tRevision year:", revision_year)
                         
                    if verbose:
                        if results[title]["citations"]:
                            input("="*50)
                        else:
                            print("="*50)

                revision_index += 1
            for title, result in results.items():
                for citation in result["citations"].values():
                    citations_csv_writer.writerow(citation)
                if len(result["citations"]) >= 10:
                    latencies = [citation[-1] for citation in result["citations"].values()]
                    latencies_csv_writer.writerow([title, result["pageid"], results[title]["title_creation_year"], len(latencies), round(mean(latencies), 2), round(std(latencies), 2)])
                    latency_file.flush()

print(datetime.now() - start)
