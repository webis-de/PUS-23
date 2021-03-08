from datetime import datetime
from article.article import Article
from differ.lcs import Differ
from preprocessor.preprocessor import Preprocessor
from multiprocessing import Pool

preprocessor = Preprocessor("en")

def get_tokenset(revision):
    return (revision.revid, revision.timestamp.string, set(preprocessor.preprocess(
        revision.get_text(), lower=False, stopping=False, sentenize=False, tokenize=True)[0]))

article = Article("../articles/2021-03-01/CRISPR_en")

authors = {"Doudna":[],"Charpentier":[],"Lander":[],"Barrangou":[],"Mojica":[]}

start = datetime.now()

with Pool() as pool:
    tokensets = pool.map(get_tokenset, article.yield_revisions())

for revid, timestamp, tokens in tokensets:
    for author in authors:
        if author in tokens:
            authors[author].append((revid, timestamp))

end = datetime.now()

print(end - start)

#print(authors)
