from entity.article import Article
from pprint import pprint, pformat
from lxml import html, etree

##########################################################
# This file serves as an entry point to test the Article.#
##########################################################

def heading(text):
    print(text)
    print("="*(len(text.replace("\n",""))))
    print()

if __name__ == "__main__":

    #Open scraped article.
    article = Article("../extractions/CRISPR_en")
    article.get_revisions(2010, 2010)
    revision = article.revisions[0]
    """
    #Print html.
    heading("HTML")
    print(pformat(revision.html, width=300))
    """
    #Print text from html.
    heading("\nTEXT")
    print(revision.get_text().strip())

    #Print all categories.
    heading("\nCATEGORIES")
    for category in revision.get_categories():
        print(category)
    
    #Print references from html.
    references = revision.get_references()
    CITATION_STYLE = "en" #citation style different for German (de) and English (en)
    authors = revision.get_referenced_authors(CITATION_STYLE)
    titles = revision.get_referenced_titles(CITATION_STYLE)
    dois = revision.get_referenced_dois()
    heading("\nREFERENCES " + "(" + str(len(references)) + ")")
    count = 1
    for reference, author, title, doi in zip(references, authors, titles, dois):
        print(str(count))
        #print(html.tostring(reference).decode("utf-8"))
        #print()
        print("".join(reference.itertext()))
        print()
        print("AUTHORS: " + str(author))
        print("TITLE: " + str(title))
        print("DOIS: " + str(doi))
        input("-"*50)
        count += 1


