from article.article import Article
from bibliography.bibliography import Bibliography
from json import load
from unicodedata import normalize

def to_ascii(string):
    return normalize("NFD",string).encode("ASCII","ignore").decode("ASCII")

bib = Bibliography("../data/tracing-innovations-lit.bib")

bib_titles = ([to_ascii(title.lower()).replace("-","").replace("/","-") for title in bib.titles])
bib_dois = ([doi.lower() for doi in bib.dois if doi])
bib_pmids = ([pmid for pmid in bib.pmids if pmid])

print("Number of Titles in tracing-innovations-lit.bib:",len(bib_titles))
print("Duplicates:", set([title for title in bib_titles if bib_titles.count(title) > 1]))
print()
print("Number of DOIs in tracing-innovations-lit.bib:",len(bib_dois))
print("Duplicates:", set([doi for doi in bib_dois if bib_dois.count(doi) > 1]))
print()
print("Number of PMIDs in tracing-innovations-lit.bib:",len(bib_pmids))
print("Duplicates:", set([pmid for pmid in bib_pmids if bib_pmids.count(pmid) > 1]))

print()

data = load(open("../articles/CRISPR_en_bib_old.json"))

article_titles = [title.replace("-","").replace("/","-") for title in data["titles"].keys()]
articles_dois = data["dois"].keys()
articles_pmids = data["pmids"].keys()

print("Number of Titles in CRISPR article (incl. near-duplicates):",len(article_titles))
print("Number of DOIs in CRISPR article:",len(articles_dois))
print("Number of PMIDs in CRISPR article:",len(articles_pmids))

print()

print("Size of intersection of titles:", len(set(bib_titles).intersection(set(article_titles))))
print("Size of intersection of DOIs:", len(set(bib_dois).intersection(set(articles_dois))))
print("Size of intersection of PMIDs:", len(set(bib_pmids).intersection(set(articles_pmids))))
