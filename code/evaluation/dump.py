from glob import glob
from csv import reader, writer
from pprint import pformat, pprint
from urllib.parse import quote, unquote

def scroll_to_url(article_name, revid, string):
    return ("https://en.wikipedia.org/w/index.php?title=" + article_name.replace(" ", "_")
            + "&oldid=" + revid
            + "#:~:text=" + quote(string))

directory = "../../analysis/articles_new/articles_candidates_from_dump/"

filepaths = glob(directory + "*results.csv")

def get_publication_data_csv():
    dois = set()
    pmids = set()
    publication_map = {}
    with open("../../data/CRISPR_literature.csv") as csvfile:
        csv_reader = reader(csvfile, delimiter="|")
        header = True
        for wos_uid, title, doi, pmid in csv_reader:
            if header:
                header = False
                continue
            if doi and doi not in publication_map:
                publication_map[doi] = wos_uid
                if doi in dois:
                    print(doi)
                dois.add(doi)
            if pmid and pmid not in publication_map:
                publication_map[pmid] = wos_uid
                if pmid in pmids:
                    print(pmid)
                pmids.add(pmid)
    print(len(dois))
    print(len(pmids))
    return publication_map

##def get_publication_data_csv():
##    publication_map = {}
##    with open("../../data/CRISPR_literature.csv") as csvfile:
##        csv_reader = reader(csvfile, delimiter="|")
##        header = True
##        for wos_uid, title, doi, pmid in csv_reader:
##            if header:
##                header = False
##                continue
##            if wos_uid not in publication_map:
##                publication_map[wos_uid] = []
##            if doi and doi not in publication_map[wos_uid]:
##                publication_map[wos_uid].append(doi)
##            if pmid and pmid not in publication_map[wos_uid]:
##                publication_map[wos_uid].append(pmid)
##    return publication_map

publication_map = get_publication_data_csv()

##for key,value in publication_map.items():
##	if len(value) > 2:
##		print(key, value)

input("DONE")

results = {}

#collect all unique occurrences of (revid,timestamp) tuples for each article and bibkey
for index, filepath in enumerate(filepaths):
    print(index + 1)
    with open(filepath) as file:
        csv_reader = reader(file,  delimiter=',')
        for doi_or_pmid, article_name, revid, timestamp in csv_reader:
            if not doi_or_pmid.startswith("10."):
                doi_or_pmid = "".join([character for character in doi_or_pmid if character.isnumeric()])
            bibkey = publication_map[doi_or_pmid]
            if article_name not in results:
                results[article_name] = {}
            if bibkey not in results[article_name]:
                results[article_name][bibkey] = {}
            if doi_or_pmid not in results[article_name][bibkey]:
                results[article_name][bibkey][doi_or_pmid] = set()
            results[article_name][bibkey][doi_or_pmid].add((revid,timestamp))

#sort articles according to descending number of publications found
results = {article_name:results[article_name]
           for article_name in sorted(results.keys(),
                                      key=lambda article_name: len(results[article_name]),
                                      reverse=True)}

#for each article and bibkey, find latest revision as per DOI or PMID
first_and_final_revision_for_article_and_bibkey_map = {}
for article_name in results:
    for bibkey in results[article_name]:
        first_doi_match = ["",""]
        final_doi_match = ["",""]
        first_pmid_match = ["",""]
        final_pmid_match = ["",""]
        for doi_or_pmid in results[article_name][bibkey]:
            if doi_or_pmid.isnumeric():
                revisions_for_pmid_sorted = sorted(results[article_name][bibkey][doi_or_pmid],
                                                   key=lambda tupl:tupl[1])
                first_pmid_match = revisions_for_pmid_sorted[0][:2]
                final_pmid_match = revisions_for_pmid_sorted[-1][:2]
            else:
                revisions_for_pmid_sorted = sorted(results[article_name][bibkey][doi_or_pmid],
                                                   key=lambda tupl:tupl[1])
                first_doi_match = revisions_for_pmid_sorted[0][:2]
                final_doi_match = revisions_for_pmid_sorted[-1][:2]
        if article_name not in first_and_final_revision_for_article_and_bibkey_map:
            first_and_final_revision_for_article_and_bibkey_map[article_name] = {}
        first_and_final_revision_for_article_and_bibkey_map[article_name][bibkey] = {"first_pmid_match":first_pmid_match,
                                                                                     "final_pmid_match":final_pmid_match,
                                                                                     "first_doi_match":first_doi_match,
                                                                                     "final_doi_match":final_doi_match}

#map (revid,timestamp) tuples to count
for article_name in results:
    for bibkey in results[article_name]:
        for doi_or_pmid in results[article_name][bibkey]:
            results[article_name][bibkey][doi_or_pmid] = len(results[article_name][bibkey][doi_or_pmid])


#sort bibkeys according to descending number of revisions encountered in first; bibkey second
results = {article_name:{bibkey:results[article_name][bibkey]
                         for bibkey in sorted(results[article_name].keys(),
                                              key=lambda bibkey: (max(results[article_name][bibkey].values()),bibkey),
                                              reverse=True)}
           for article_name in results}

#write to txt
with open(directory + "articles_analysis.txt", "w") as file:
    file.write(pformat(results, sort_dicts=False))
#write to csv
with open(directory + "articles_analysis.csv", "w") as file:
    csv_writer = writer(file, delimiter=",")
    for article_name in results:
        first_time_article_name = True
        for bibkey in results[article_name]:
            pmid = ""
            pmid_count = ""
            doi = ""
            doi_count = ""
            for doi_or_pmid, count in results[article_name][bibkey].items():
                if doi_or_pmid.isnumeric():
                    pmid = doi_or_pmid
                    pmid_count = count
                else:
                    doi = doi_or_pmid
                    doi_count = count
            revid_of_first_pmid_match,timestamp_of_first_pmid_match = first_and_final_revision_for_article_and_bibkey_map[article_name][bibkey]["first_pmid_match"]
            revid_of_final_pmid_match,timestamp_of_final_pmid_match = first_and_final_revision_for_article_and_bibkey_map[article_name][bibkey]["final_pmid_match"]
            revid_of_first_doi_match,timestamp_of_first_doi_match = first_and_final_revision_for_article_and_bibkey_map[article_name][bibkey]["first_doi_match"]
            revid_of_final_doi_match,timestamp_of_final_doi_match = first_and_final_revision_for_article_and_bibkey_map[article_name][bibkey]["final_doi_match"]
            csv_writer.writerow([article_name if first_time_article_name else "",
                                 bibkey,
                                 doi,
                                 doi_count,
                                 revid_of_first_doi_match,
                                 timestamp_of_first_doi_match,
                                 scroll_to_url(article_name,
                                               revid_of_first_doi_match,
                                               doi) if doi else "",
                                 revid_of_final_doi_match,
                                 timestamp_of_final_doi_match,
                                 scroll_to_url(article_name,
                                               revid_of_final_doi_match,
                                               doi) if doi else "",
                                 "---",
                                 pmid,
                                 pmid_count,
                                 revid_of_first_pmid_match,
                                 timestamp_of_first_pmid_match,
                                 scroll_to_url(article_name,
                                               revid_of_first_pmid_match,
                                               pmid) if pmid else "",
                                 revid_of_final_pmid_match,
                                 timestamp_of_final_pmid_match,
                                 scroll_to_url(article_name,
                                               revid_of_final_pmid_match,
                                               pmid) if pmid else "",
                                 "---"])
            first_time_article_name = False

print(directory)
