from csv import reader
from glob import glob
import tarfile
import gzip

identifiers = set()
with open("../data/CRISPR_literature_final.csv") as file:
    csv_reader = reader(file, delimiter="|")
    print(next(csv_reader))
    for WOS_UID, TITLE, AUTHORS, DOI, PMID, YEAR in csv_reader:
        if DOI: identifiers.add(DOI)
        if PMID: identifiers.add(PMID)

with open("../data/CRISPR_articles_849.txt") as file:
    articles849 = set([article.strip() for article in file.readlines()])

#########################
        
tarballs = glob("../citationcorpora/citationcorpus1/*.tar.gz")
article_titles_corpus1 = set()
for index, tarball in enumerate(tarballs, 1):
    print(index, len(tarballs))
    with tarfile.open(tarball, "r:gz") as tarfile:
        for member in tarfile.getmembers():
            for line in tarfile.extractfile(member):
                page_id, page_title, rev_id, timestamp, TYPE, ID = line.decode("utf-8").strip().split("\t")
                if ID in identifiers:
                    article_titles_corpus1.add(page_title)

print(len(articles849.difference(article_titles_corpus1)))
print(len(article_titles_corpus1.difference(articles849)))

#########################

tarballs = glob("../citationcorpora/citationcorpus2/*.tsv.gz")
article_titles_corpus2 = set()
for index, tarball in enumerate(tarballs, 1):
    print(index, len(tarballs))
    with gzip.open(tarball, 'rb') as tarfile:
        for line in tarfile:
            page_id, page_name, revision_id, timestamp, publication_type, publication_id, topic, open_access, open_access_url = line.decode("utf-8").split("\t")
            if publication_id in identifiers:
                article_titles_corpus2.add(page_name)
                
print(len(articles849.difference(article_titles_corpus2)))
print(len(article_titles_corpus2.difference(articles849)))



