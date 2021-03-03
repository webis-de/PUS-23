from article.article import Article
from pprint import pprint, pformat

article = Article("../articles/2021-02-14/CRISPR_en")

#revision = article.get_revision(revid=603963726)
revision = article.get_revision(revid=701817377)
print(revision.index)
print(revision.url, "\n")

with open("sections.txt", "w") as file:
    tree = revision.section_tree()
    file.write(pformat(tree.json(), width=200, sort_dicts=False))

history = tree.subsections[0]
href = '#cite_note-13'
##print(history.text(include_heading=True))

##with open("sections.txt", "a") as file:
##    file.write("\n\n" + ("="*100) + "\n\n")
##    tree = revision.tree().find(["History"])
##    file.write(pformat([section.json() for section in tree], width=200, sort_dicts=False))
