import matplotlib.pyplot as plt
from json import load
import numpy as np

HINT = 0.2

def calculate_delay(match_year, event_year):
    if match_year:
        return max(HINT, match_year - event_year + 1)
    else:
        return HINT

def stringify_delay(delay):
    if delay == HINT:
        return "-".rjust(20, " ")
    else:
        return str(delay - 1).rjust(20, " ")

data = sorted([event for event in load(open("../analysis/DE_TEST/2021_01_21_12_09_09/CRISPR_de.json")) if event["type"] == "publication" and event["bibentries"]], key=lambda event: int(event["event_year"]))

bibkey = [list(event["bibentries"].keys())[0] for event in data]
event_years = [int(event["event_year"]) if event["event_year"] else None for event in data]
title_exact_matches = [int(event["first_mentioned"]["titles"]["exact_match"]["timestamp"][:4]) if event["first_mentioned"]["titles"]["exact_match"] else None for event in data]
title_ned_matches = [int(event["first_mentioned"]["titles"]["ned"]["timestamp"][:4]) if event["first_mentioned"]["titles"]["ned"] else None for event in data]
authors_exact_matches = [int(event["first_mentioned"]["authors"]["exact_match"]["timestamp"][:4]) if event["first_mentioned"]["authors"]["exact_match"] else None for event in data]
authors_ndcg_matches = [int(event["first_mentioned"]["authors"]["ndcg"]["timestamp"][:4]) if event["first_mentioned"]["authors"]["ndcg"] else None for event in data]
authors_jaccard_matches = [int(event["first_mentioned"]["authors"]["jaccard"]["timestamp"][:4]) if event["first_mentioned"]["authors"]["jaccard"] else None for event in data]
doi_matches = [int(event["first_mentioned"]["dois"]["timestamp"][:4]) if event["first_mentioned"]["dois"] else None for event in data]
pmid_matches = [int(event["first_mentioned"]["pmids"]["timestamp"][:4]) if event["first_mentioned"]["pmids"] else None for event in data]

if True:
    lists = [title_ned_matches, authors_exact_matches, authors_ndcg_matches, authors_jaccard_matches, doi_matches, pmid_matches]

    bibkey_reduced = [bibkey[i] for i in range(len(event_years)) if len([l[i] for l in lists if l[i]]) != 0]
    event_years_reduced = [event_years[i] for i in range(len(event_years)) if len([l[i] for l in lists if l[i]]) != 0]
    title_exact_matches_reduced = [title_exact_matches[i] for i in range(len(event_years)) if len([l[i] for l in lists if l[i]]) != 0]
    title_ned_matches_reduced = [title_ned_matches[i] for i in range(len(event_years)) if len([l[i] for l in lists if l[i]]) != 0]
    authors_exact_matches_reduced = [authors_exact_matches[i] for i in range(len(event_years)) if len([l[i] for l in lists if l[i]]) != 0]
    authors_ndcg_matches_reduced = [authors_ndcg_matches[i] for i in range(len(event_years)) if len([l[i] for l in lists if l[i]]) != 0]
    authors_jaccard_matches_reduced = [authors_jaccard_matches[i] for i in range(len(event_years)) if len([l[i] for l in lists if l[i]]) != 0]
    doi_matches_reduced = [doi_matches[i] for i in range(len(event_years)) if len([l[i] for l in lists if l[i]]) != 0]
    pmid_matches_reduced = [pmid_matches[i] for i in range(len(event_years)) if len([l[i] for l in lists if l[i]]) != 0]

    bibkey = bibkey_reduced
    event_years = event_years_reduced
    title_exact_matches = title_exact_matches_reduced
    title_ned_matches = title_ned_matches_reduced
    authors_exact_matches = authors_exact_matches_reduced
    authors_ndcg_matches = authors_ndcg_matches_reduced
    authors_jaccard_matches = authors_jaccard_matches_reduced
    doi_matches = doi_matches_reduced
    pmid_matches = pmid_matches_reduced

print("bibkey".rjust(20, " "),
      "event_year".rjust(10, " "),
      "title_exact".rjust(20, " "),
      "title_ned".rjust(20, " "),
      "authors_exact".rjust(20, " "),
      "authors_ndcg".rjust(20, " "),
      "authors_jaccard".rjust(20, " "),
      "doi".rjust(20, " "),
      "pmid".rjust(20, " "))
for bibkey, event_year, title_exact_match, title_ned_match, authors_exact_match, authors_ndcg_match, authors_jaccard_match, doi_match, pmid_match in \
    zip(bibkey, event_years, title_exact_matches, title_ned_matches, authors_exact_matches, authors_ndcg_matches, authors_jaccard_matches, doi_matches, pmid_matches):
    print(str(bibkey).rjust(20, " "),
          str(event_year).rjust(10, " "),
          stringify_delay(calculate_delay(title_exact_match, event_year)),
          stringify_delay(calculate_delay(title_ned_match, event_year)),
          stringify_delay(calculate_delay(authors_exact_match, event_year)),
          stringify_delay(calculate_delay(authors_ndcg_match, event_year)),
          stringify_delay(calculate_delay(authors_jaccard_match, event_year)),
          stringify_delay(calculate_delay(doi_match, event_year)),
          stringify_delay(calculate_delay(pmid_match, event_year)))

title_exact_delays = [calculate_delay(match, year) for match,year in zip(title_exact_matches, event_years)]
title_ned_delays = [calculate_delay(match, year) for match,year in zip(title_ned_matches, event_years)]
authors_exact_delays = [calculate_delay(match, year) for match,year in zip(authors_exact_matches, event_years)]
authors_ndcg_delays = [calculate_delay(match, year) for match,year in zip(authors_ndcg_matches, event_years)]
authors_jaccard_delays = [calculate_delay(match, year) for match,year in zip(authors_jaccard_matches, event_years)]
doi_delays = [calculate_delay(match, year) for match,year in zip(doi_matches, event_years)]
pmid_delays = [calculate_delay(match, year) for match,year in zip(pmid_matches, event_years)]

event_years = [str(year) for year in event_years]
year = event_years[0]
for i in range(1, len(event_years)):
    if event_years[i] == year:
        event_years[i] = ""
    else:
        year = event_years[i]

width = 0.1
x = np.arange(len(event_years))
plt.figure(figsize=(50, 3), dpi=150)
plt.subplots_adjust(bottom=0.15, top=0.99, left=0.01, right=0.998)
plt.margins(x=0.0005, y=0.005)
plt.xticks(np.arange(len(event_years)), event_years)
plt.xlabel("PUBLICATIONS  (colours reprensent different metrics as per legend; years + 1, e.g. a column of height 1 means the publication occurred the same year; column hints for visualistion represent no occurrence)")
plt.ylabel("OCCURRENCE DELAY IN YEARS")
plt.bar(x - width*3, title_exact_delays, width=width, label="title_exact")
plt.bar(x - width*2, title_ned_delays, width=width, label="title_ned")
plt.bar(x - width, authors_exact_delays, width=width, label="authors_exact")
plt.bar(x, authors_ndcg_delays, width=width, label="authors_ndcg")
plt.bar(x + width, authors_jaccard_delays, width=width, label="authors_jaccard")
plt.bar(x + width*2, doi_delays, width=width, label="doi")
plt.bar(x + width*3, pmid_delays, width=width, label="pmid")
plt.legend()
plt.savefig("delays.png")
