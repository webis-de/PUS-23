from entity.revision.revision import Revision
from entity.timestamp import Timestamp
from random import randint
from json import loads

#################################################################
# This file serves as an entry point to test the Revision class.#
#################################################################

def heading(text):
    print(text)
    print("="*(len(text.replace("\n",""))))
    print()

if __name__ == "__main__":

    #Select a language: en or de
    LANGUAGE = "en"

    #Open scraped article and get random revision.
    random_index = randint(0,2023)
    line = 0
    with open("../extractions/CRISPR_" + LANGUAGE) as article:
        while line < random_index:
            article.readline()
            line += 1
        revision = Revision(**loads(article.readline()))

    print("You are looking at revision number " + str(random_index) + " from " + Timestamp(revision.timestamp).string + ".")
    #URL of revsions
    heading("\nURL OF REVISION")
    print(revision.url)

    #Print text from html
    heading("\nTEXT")
    print(revision.get_text().strip())

    #Print paragraphs from html
    heading("\nPARAGRAPHS")
    print("\n".join([paragraph.text() for paragraph in revision.get_paragraphs()]))

    #Print all categories.
    heading("\nCATEGORIES")
    for category in revision.get_categories():
        print(category)
    
    #Print references and further reading from html.
    CITATION_STYLE = LANGUAGE #citation style different for German (de) and English (en)
    sources = {"REFERENCES": revision.get_references(), "FURTHER READING":revision.get_further_reading()}
    for source in sources.items():
        authors = revision.get_referenced_authors(CITATION_STYLE, source[1])
        titles = revision.get_referenced_titles(CITATION_STYLE, source[1])
        dois = revision.get_referenced_dois(source[1])
        heading("\n" + source[0] + " " + "(" + str(len(source[1])) + ")")
        for reference, author, title, doi in zip(source[1], authors, titles, dois):
            print("NUMBER: " + str(reference.number))
            print("REFERENCE TEXT: " + reference.text().strip())
            print()
            print("AUTHORS: " + str(author))
            print("TITLE: " + str(title))
            print("DOIS: " + str(doi))
            print("\nLINKED PARAGRAPHS:")
            backlinks = reference.backlinks()
            if backlinks:
                print("\n".join(["=>" + str(backlink) + "\n" + linked_paragraph.text().strip() for backlink, linked_paragraph in zip(backlinks, reference.linked_paragraphs(revision.get_paragraphs()))]))
            input("-"*50)
