from glob import glob
from csv import reader, writer
from pprint import pformat
from urllib.parse import quote, unquote

def scroll_to_url(article_name, revid, string):
    return ("https://en.wikipedia.org/w/index.php?title=" + article_name.replace(" ", "_")
            + "&oldid=" + revid
            + "#:~:text=" + quote(string))

filepaths = glob("../../analysis/dump_thorough/*results.csv")

results = {}
corpus_map = {}

#collect all unique occurrences of (revid,timestamp,corpus) tuples for each article and bibkey
for index, filepath in enumerate(filepaths):
    print(index + 1)
    with open(filepath) as file:
        csv_reader = reader(file,  delimiter=',')
        for bibkey, doi_or_pmid, article_name, revid, timestamp, corpus in csv_reader:
            if article_name not in results:
                results[article_name] = {}
            if bibkey not in results[article_name]:
                results[article_name][bibkey] = {}
            if doi_or_pmid not in results[article_name][bibkey]:
                results[article_name][bibkey][doi_or_pmid] = set()
            results[article_name][bibkey][doi_or_pmid].add((revid,timestamp,corpus))
            if bibkey not in corpus_map:
                corpus_map[bibkey] = {"wos":"","accounts":""}
            for subcorpus in corpus.split("|"):
                corpus_map[bibkey][subcorpus] = "X"

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
                                                                           
      
###collate results in results.csv
##with open("results.csv", "w", newline="") as coalated_file:
##    csv_writer = writer(coalated_file, delimiter=",")
##    for article_name in results:
##        first_time_article_name = True
##        for bibkey in results[article_name]:
##            first_time_bibkey = True
##            for doi_or_pmid in results[article_name][bibkey]:
##                for revid,timestamp,corpus in results[article_name][bibkey][doi_or_pmid]:
##                    csv_writer.writerow([article_name if first_time_article_name else "",
##                                         bibkey if first_time_bibkey else "",
##                                         doi_or_pmid,
##                                         revid,
##                                         timestamp,
##                                         corpus])
##                    first_time_article_name = False
##                first_time_bibkey = False

#map (revid,timestamp,corpus) tuples to count
for article_name in results:
    for bibkey in results[article_name]:
        for doi_or_pmid in results[article_name][bibkey]:
            results[article_name][bibkey][doi_or_pmid] = len(results[article_name][bibkey][doi_or_pmid])


#sort bibkeys according to descending number of revisions encountered in
results = {article_name:{bibkey:results[article_name][bibkey]
                         for bibkey in sorted(results[article_name].keys(),
                                              key=lambda bibkey: max(results[article_name][bibkey].values()),
                                              reverse=True)}
           for article_name in results}

#print to results.txt
with open("results_basic.txt", "w") as file:
    file.write(pformat(results, sort_dicts=False))
with open("results_basic.csv", "w") as file:
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
                                 corpus_map[bibkey]["wos"],
                                 corpus_map[bibkey]["accounts"],
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
            
##with open("wikipedia_dump_analysis.txt", "w") as file:
##    for article_name in results:
##        file.write(article_name + "\n")
##        for bibkey in results[article_name]:
##            file.write("\t" + "bibkey: ".ljust(11, " ") + bibkey + "\n")
##            for doi_or_pmid in results[article_name][bibkey]:
##                file.write("\t" + ("PMID:" if doi_or_pmid.isnumeric() else "DOI:").ljust(11, " ") + doi_or_pmid + "\n")
##                for key,value in results[article_name][bibkey][doi_or_pmid].items():
##                    file.write("\t" + key.ljust(11, " ") + value.replace("|", ", ") + "\n")
