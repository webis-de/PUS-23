from article.article import Article
from bibliography.bibliography import Bibliography
from json import load
from unicodedata import normalize

def to_ascii(string):
    return normalize("NFD",string).encode("ASCII","ignore").decode("ASCII")

def to_lower(string):
    return string.lower()

def to_alnum(string):
    return "".join([character for character in string if character.isalnum() or character in [" "]])

bibliography = Bibliography("../data/tracing-innovations-lit.bib")
article = Article("../articles/CRISPR_en")

article.bibliography_analysis()

bibliography_titles = ([to_alnum(to_lower(to_ascii(title))).strip() for title in bibliography.titles])
bibliography_dois = ([doi.lower() for doi in bibliography.dois if doi])
bibliography_pmids = ([pmid for pmid in bibliography.pmids if pmid])

print("Number of Titles in tracing-innovations-lit.bib:",len(bibliography_titles))
print("Duplicates:", set([title for title in bibliography_titles if bibliography_titles.count(title) > 1]))
print()
print("Number of DOIs in tracing-innovations-lit.bib:",len(bibliography_dois))
print("Duplicates:", set([doi for doi in bibliography_dois if bibliography_dois.count(doi) > 1]))
print()
print("Number of PMIDs in tracing-innovations-lit.bib:",len(bibliography_pmids))
print("Duplicates:", set([pmid for pmid in bibliography_pmids if bibliography_pmids.count(pmid) > 1]))

print()

data = load(open("../articles/CRISPR_en_bib.json"))

article_titles = [to_alnum(to_lower(to_ascii(title))).strip() for title in data["titles"].keys()]
articles_dois = data["dois"].keys()
articles_pmids = data["pmids"].keys()

print("Number of Titles in CRISPR article (incl. near-duplicates):",len(article_titles))
print("Number of DOIs in CRISPR article:",len(articles_dois))
print("Number of PMIDs in CRISPR article:",len(articles_pmids))

print()

print("Size of intersection of titles:", len(set(bibliography_titles).intersection(set(article_titles))))
print("Size of intersection of DOIs:", len(set(bibliography_dois).intersection(set(articles_dois))))
print("Size of intersection of PMIDs:", len(set(bibliography_pmids).intersection(set(articles_pmids))))
