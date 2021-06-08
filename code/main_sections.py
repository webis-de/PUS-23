from article.article import Article
from preprocessor.preprocessor import Preprocessor
from pprint import pprint, pformat

####################################################################
# This file serves as an entry point to analyse Wikipedia sections.#
####################################################################

article = Article("../articles/2021-03-01/CRISPR_en")

revision = article.get_revision(index=1200)
preprocessor = Preprocessor("en")

with open("section_tree.txt", "w") as file:
    file.write("Revision Index\n\n")
    file.write(str(revision.index))
    file.write("\n" + ("="*100) + "\n")

    file.write("Revision URL\n\n")
    file.write(revision.url)
    file.write("\n" + ("="*100) + "\n")
    
    file.write("Revision Section Tree\n\n")
    section_tree = revision.section_tree(article.name)
    file.write(pformat(section_tree.json(), width=200, sort_dicts=False))
    file.write("\n\n" + ("="*100) + "\n")

    SECTION_NAMES = ["History"]

    TITLE = ", ".join(SECTION_NAMES)
    
    file.write(TITLE + " Section\n\n")
    
    SECTIONS = section_tree.find(SECTION_NAMES)

    if SECTIONS:
        SECTION_TREE = SECTIONS[0]
        file.write(pformat(SECTION_TREE.json(), width=200, sort_dicts=False) + "\n\n")

        file.write("Titles and Authors in " + TITLE + " Section\n\n")
        for source in SECTION_TREE.get_sources(revision.get_references(), 1):
            file.write(source.get_title("en") + "\n")
            file.write(str(source.get_authors("en")) + "\n\n")
    else:
        file.write("NO " + TITLE + " SECTION")

    text = section_tree.find([""])[0].get_text(10, with_headings=True)
    print(text)
    print(preprocessor.preprocess(text, False, False, False, True))
    print([s.name for s in section_tree.find(["Re"])])
