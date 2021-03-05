from article.article import Article
from differ.lcs import Differ
from difflib import Differ
import matplotlib.pyplot as plt
from datetime import datetime
import numpy as np

article = Article("../articles/2021-03-01/CRISPR_gene_editing_en")

differ = Differ()

timestamps = []
added_characters = []
removed_characters = []
sizes = []

##revid1 = 942550392
##revid2 = 942551764
##
##rev1 = article.get_revision(revid=revid1).section_tree().find(["History"])[0].get_text(6)
##rev2 = article.get_revision(revid=revid2).section_tree().find(["History"])[0].get_text(6)
##start = datetime.now()
##differ.compare(rev1, rev2)
##end = datetime.now()
##print(end - start)
##print(1 + "")

revision_iterator = article.yield_revisions()

old_string = ""
revision = next(revision_iterator, None)

while revision:
    print(revision.index)
    print(revision.url)
    section_tree = revision.section_tree()
    history_sections = section_tree.find(["History"])
    if history_sections:
        new_string = history_sections[0].get_text(6)
    else:
        new_string = ""
    diff = differ.compare(old_string, new_string)
    timestamp = str(revision.timestamp.month).rjust(2,"0") + "/" + str(revision.timestamp.year)
    timestamps.append("" if timestamp in timestamps else timestamp)
    added = 0
    removed = 0
    for item in diff:
        if item[0] == "+":
            added += 1
        if item[0] == "-":
            removed += 1
    added_characters.append(added)
    removed_characters.append(removed)
    sizes.append(len(new_string))
    print("="*50)

    old_string = new_string

    revision = next(revision_iterator, None)

plt.figure(figsize=(25, 5), dpi=250)
plt.subplots_adjust(bottom=0.15, top=0.95, left=0.01, right=0.99)
plt.margins(x=0)
plt.bar(np.arange(len(added_characters)) - 0.15, added_characters, width=0.3, label="added characters")
plt.bar(np.arange(len(removed_characters)) + 0.15, removed_characters, width=0.3, label="removed characters")
plt.plot(list(range(len(sizes))), sizes, label="section size", color="green")
plt.xticks(list(range(len(timestamps))), timestamps, rotation = 90)
plt.title("History Section " + article.name)
plt.legend()
plt.savefig("History Section " + article.name + ".png")

