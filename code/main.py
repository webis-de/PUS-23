from article.article import Article
from differ.lcs import Differ
import matplotlib.pyplot as plt
from datetime import datetime

article = Article("../articles/2021-03-01/CRISPR_gene_editing_en")

differ = Differ()

timestamps = []
added = []
removed = []
sizes = []

##revid1 = 942550392
##revid2 = 942551764
##
##rev1 = article.get_revision(revid=revid1).section_tree().find(["History"])[0].get_text(6)
##
##rev2 = article.get_revision(revid=revid2).section_tree().find(["History"])[0].get_text(6)
##
##start = datetime.now()
##
##differ.compare(rev1, rev2)
##
##end = datetime.now()
##
##print(end - start)
##
##print(1 + "")

revision_iterator = article.yield_revisions()

old_string = ""
revision = next(revision_iterator, None)

while revision.index:
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
    added.append(len([item for item in diff if item[0] == "+"]))
    removed.append(len([item for item in diff if item[0] == "-"]))
    sizes.append(len(new_string))
    print("="*50)

    old_string = new_string

    revision = next(revision_iterator, None)

plt.figure(figsize=(20, 5), dpi=500)
plt.subplots_adjust(bottom=0.15, top=0.95, left=0.05, right=0.95)
plt.tight_layout()
plt.xticks(list(range(len(timestamps))), timestamps, rotation = 90)
plt.plot(list(range(len(added))), added, label="added characters")
plt.plot(list(range(len(removed))), removed, label="removed characters")
plt.plot(list(range(len(sizes))), sizes, label="section size")
plt.title("History Section " + article.name)
plt.legend()
plt.savefig("History Section " + article.name + ".png")
