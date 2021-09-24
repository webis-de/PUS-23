from glob import glob
from csv import reader
from pprint import pprint

filepaths = glob("../../analysis/dump_quick/*results.csv")

results = {}

for filepath in filepaths:
    #print(filepath)
    with open(filepath) as file:
        csv_reader = reader(file,  delimiter=',')
        for bibkey, doi_or_pmid, article_name, revid, timestamp, corpus \
            in csv_reader:
            if article_name not in results:
                results[article_name] = {}
            if bibkey not in results[article_name]:
                results[article_name][bibkey] = {}
            if doi_or_pmid not in results[article_name][bibkey]:
                results[article_name][bibkey][doi_or_pmid] = 0
            results[article_name][bibkey][doi_or_pmid] += 1

article_names_to_delete = set()

for article_name, bibkeys in results.items():
    delete_article_name = True
    for bibkey, dois_or_pmids in bibkeys.items():
        for doi_or_pmid, count in dois_or_pmids.items():
            if len(dois_or_pmids) == 1 and count == 1:
                break
            if not doi_or_pmid.isnumeric():
                delete_article_name = False
                break
        if not delete_article_name:
            break
    if delete_article_name:
        article_names_to_delete.add(article_name)

##for article_name in article_names_to_delete:
##    del results[article_name]

results = {article_name:list(list(results[article_name].values())[0].keys())[0]
           for article_name in sorted(results.keys(),
                                      key=lambda article_name: article_name,
                                      reverse=False)}           
            
for key, value in results.items():
    print(key + ": " + value)
