from article.article import Article
from differ.lcs import Differ

article = Article("../articles/CRISPR_en")

differ = Differ()

LCSs = []

revision_iterator = article.yield_revisions()

revision = next(revision_iterator, None)
section_tree = revision.section_tree()
history_sections = section_tree.find(["History"])
if history_sections:
    old_string = history_sections[0].get_text()
else:
    old_string = ""

revision = next(revision_iterator, None)

while revision:
    print(revision.index)
    print(revision.url)
    section_tree = revision.section_tree()
    history_sections = section_tree.find(["History"])
    if history_sections:
        new_string = history_sections[0].get_text()
    else:
        new_string = ""
    LCSs.append(differ.lcs(old_string, new_string))
    print("="*50)

    old_string = new_string

    revision = next(revision_iterator, None)
    
