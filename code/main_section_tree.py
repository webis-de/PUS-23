from article.article import Article
from pprint import pprint, pformat

article = Article("../articles/2021-02-14/CRISPR_en")

revision = article.get_revision(revid=701817377)
print(revision.index)
print(revision.url)

with open("sections.txt", "w") as file:
    tree = revision.tree()
    file.write(pformat(tree.json(), width=200, sort_dicts=False))

with open("sections.txt", "a") as file:
    file.write("\n\n" + ("="*100) + "\n\n")
    tree = revision.tree().find(["Intro"])
    file.write(pformat([section.json() for section in tree], width=200, sort_dicts=False))
