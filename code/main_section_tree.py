from article.article import Article
from pprint import pprint, pformat

article = Article("../articles/2021-02-14/CRISPR_gene_editing_en")

revision = article.get_revision(index=0,revid=723879518)

with open("sections.txt", "w") as file:
    file.write("Revision Index\n\n")
    file.write(str(revision.index))
    file.write("\n" + ("="*100) + "\n")

    file.write("Revision URL\n\n")
    file.write(revision.url)
    file.write("\n" + ("="*100) + "\n")
    
    file.write("Revision Section Tree\n\n")
    section_tree = revision.section_tree()
    file.write(pformat(section_tree.json(), width=200, sort_dicts=False))
    file.write("\n\n" + ("="*100) + "\n")
    
    file.write("History Section\n\n")
    
    history_sections = section_tree.find(["History"])

    if history_sections:
        history_section_tree = history_sections[0]
        file.write(pformat(history_section_tree.json(), width=200, sort_dicts=False) + "\n\n")

        file.write("Titles and Authors in History Section\n\n")
        for source in history_section_tree.get_sources(revision.get_references()):
            file.write(source.get_title("en") + "\n")
            file.write(str(source.get_authors("en")) + "\n\n")
    else:
        file.write("NO HISTORY SECTION")
