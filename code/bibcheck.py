from article.article import Article
from json import dump

article = Article("../articles/CRISPR_en")

revisions = article.yield_revisions()

revision = next(revisions, None)

bib = {"titles":{}, "dois":{}, "pmids":{}}

while revision:
    print(revision.index)
    for source in revision.get_references() + revision.get_further_reading():
        #add title  in source if 80 percent of non-whitespace characters are alphabetic
        title = source.get_title("en")
        if title:
            if title not in bib["titles"]:
                if len([c for c in title.replace(" ","") if c.isalpha()])/len(title) > 0.8:
                    bib["titles"][title] = source.get_text()
        #add DOIs in source
        doi_set = source.get_dois()
        for doi in doi_set:
            if doi not in bib["dois"]:
                bib["dois"][doi] = source.get_text()
        #add PMIDs  in source
        pmid_set = source.get_pmids()
        for pmid in pmid_set:
            if pmid not in bib["pmids"]:
                bib["pmids"][pmid] = source.get_text()
    revision = next(revisions, None)

with open("bibcheck.json", "w") as file:
    dump(bib, file)
