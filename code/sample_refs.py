from article.article import Article
from random import sample
from glob import glob

files = glob("../articles/2021-06-01_with_html/en/CRISPR*_en")

refs = []

for file in files:

    art = Article(file)

    print(file)

    for rev in art.yield_revisions():
        if rev.index % 100 == 0: print(rev.index)
        for ref in rev.get_references():
            refs.append(ref)

print(len(refs))

samples = sample(refs, 5000)

with open("sampled_refs.txt", "w") as file:
    for ref in samples:
        file.write(ref.get_text())
        file.write("\n\n")
        file.write(str(ref.get_authors("en")))
        file.write("\n")
        file.write("="*50)
        file.write("\n")
