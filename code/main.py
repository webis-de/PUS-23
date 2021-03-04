from article.article import Article
from differ.lcs import Differ
import matplotlib.pyplot as plt

article = Article("../articles/2021-03-01/CRISPR_gene_editing_en")

differ = Differ()

timestamps = []
added = []
removed = []

revision_iterator = article.yield_revisions()

revision = next(revision_iterator, None)
section_tree = revision.section_tree()
history_sections = section_tree.find(["History"])
if history_sections:
    old_string = history_sections[0].get_text(6)
else:
    old_string = ""
timestamps.append(str(revision.timestamp.month).rjust(2,"0") + "/" + str(revision.timestamp.year))

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
    if timestamp in timestamps:
        timestamps.append("")
    else:
        timestamps.append(timestamp)
    added.append(len([item for item in diff if item[0] == "+"]))
    removed.append(len([item for item in diff if item[0] == "-"]))
    print("="*50)

    old_string = new_string

    revision = next(revision_iterator, None)

plt.figure(figsize=(20, 5), dpi=500)
plt.subplots_adjust(bottom=0.15, top=0.95, left=0.05, right=0.95)
plt.tight_layout()
plt.plot(list(range(len(added))), added, label="added")
plt.plot(list(range(len(removed))), removed, label="removed")
plt.xticks(list(range(len(timestamps))), timestamps, rotation = 90)
plt.title("History Section " + article.name)
plt.legend()
plt.savefig("History Section " + article.name + ".png")
