from glob import glob
from csv import reader, writer
from pprint import pformat

filepaths = glob("../../analysis/dump_thorough/*results.csv")

results = {}

with open("wikipedia_dump_results_collated.csv", "w", newline="") as coalated_file:
    csv_writer = writer(coalated_file, delimiter=",")
    for index, filepath in enumerate(filepaths):
        raise_duplicate = True
        print(index + 1)
        with open(filepath) as file:
            csv_reader = reader(file,  delimiter=',')
            try:
                for bibkey, doi_or_pmid, article_name, revid, timestamp, corpus \
                    in csv_reader:
                    #csv_writer.writerow([bibkey, doi_or_pmid, article_name, revid, timestamp, corpus])
                    if article_name not in results:
                        results[article_name] = {}
                    if bibkey not in results[article_name]:
                        results[article_name][bibkey] = {}
                    if doi_or_pmid not in results[article_name][bibkey]:
                        results[article_name][bibkey][doi_or_pmid] = set()
                    else:
                        pass#print("Duplicate: ", bibkey, doi_or_pmid)
                    if revid not in results[article_name][bibkey][doi_or_pmid]:
                        results[article_name][bibkey][doi_or_pmid].add(revid)
                    else:
                        if raise_duplicate:
                            print("Duplicate revid", revid, "in filepath", filepath)
                            raise_duplicate = False
            except:
                print("Error reading", filepath)

##article_names_to_delete = set()
##for article_name, bibkeys in results.items():
##    delete_article_name = True
##    for bibkey, dois_or_pmids in bibkeys.items():
##        for doi_or_pmid, count in dois_or_pmids.items():
##            if len(dois_or_pmids) == 1 and count == 1:
##                break
##            if not doi_or_pmid.isnumeric():
##                delete_article_name = False
##                break
##        if not delete_article_name:
##            break
##    if delete_article_name:
##        article_names_to_delete.add(article_name)
##
##for article_name in article_names_to_delete:
##    del results[article_name]

results = {article_name:results[article_name]#list(list(results[article_name].values())[0].keys())[0]
           for article_name in sorted(results.keys(),
                                      key=lambda article_name: len(results[article_name]),
                                      reverse=True)}

for article_name in results:
    for bibkey in results[article_name]:
        for doi_or_pmid in results[article_name][bibkey]:
            results[article_name][bibkey][doi_or_pmid] = len(results[article_name][bibkey][doi_or_pmid])

with open("results.txt", "w") as file:
    file.write(pformat(results, sort_dicts=False))
            
##with open("wikipedia_dump_analysis.txt", "w") as file:
##    for article_name in results:
##        file.write(article_name + "\n")
##        for bibkey in results[article_name]:
##            file.write("\t" + "bibkey: ".ljust(11, " ") + bibkey + "\n")
##            for doi_or_pmid in results[article_name][bibkey]:
##                file.write("\t" + ("PMID:" if doi_or_pmid.isnumeric() else "DOI:").ljust(11, " ") + doi_or_pmid + "\n")
##                for key,value in results[article_name][bibkey][doi_or_pmid].items():
##                    file.write("\t" + key.ljust(11, " ") + value.replace("|", ", ") + "\n")
