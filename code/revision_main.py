from entity.revision.revision import Revision
from entity.timestamp import Timestamp
from random import randint
from json import loads
from re import sub

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
    random_index = 1935#randint(0,2023)
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
    paragraphs = revision.get_paragraphs()
    print(sub(r"\n\n+", "\n\n", "\n\n".join([section.text() for section in paragraphs])))

    #Print headings from html
    heading("\nHEADINGS")
    headings = revision.get_headings()
    print(sub(r"\n\n+", "\n\n", "\n\n".join([section.text() for section in headings])))

    #Print lists from html
    heading("\nLISTS")
    lists = revision.get_lists()
    print(sub(r"\n\n+", "\n\n", "\n\n".join([section.text() for section in lists])))

    #Print captions from html
    heading("\nCAPTIONS")
    captions = revision.get_captions()
    print(sub(r"\n\n+", "\n\n", "\n\n".join([section.text() for section in captions])))

    #Print tables from html
    heading("\nTABLES")
    tables = revision.get_tables()
    print(sub(r"\n\n+", "\n\n", "\n\n".join([section.text() for section in tables])))

    #Print all categories.
    heading("\nCATEGORIES")
    for category in revision.get_categories():
        print(category)
    
    #Print references and further reading from html.
    CITATION_STYLE = LANGUAGE #citation style different for German (de) and English (en)
    sources = {"REFERENCES": revision.get_references(), "FURTHER READING":revision.get_further_reading()}
    sections = paragraphs + headings + lists + captions + tables
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
                print("\n".join(["=>" + str(backlink) + "\n" + linked_section.text().strip() for backlink, linked_section in zip(backlinks, reference.linked_sections(sections))]))
            else:
                print("-")
            input("-"*50)
