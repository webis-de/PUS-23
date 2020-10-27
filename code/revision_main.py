from entity.revision.revision import Revision
from entity.timestamp import Timestamp
from random import randint
from json import loads
from re import sub
from datetime import datetime

#################################################################
# This file serves as an entry point to test the Revision class.#
#################################################################

def heading(text, file):
    file.write(text + "\n")
    file.write("="*(len(text.replace("\n",""))) + "\n")
    file.write("\n")

if __name__ == "__main__":

    processing = ["","_raw","_preprocessor","_spacy"][0]

    with open("revision_extraction" + processing + ".txt", "w", encoding="utf-8") as file:

        #Select a language: en or de
        LANGUAGE = "en"

        #Open scraped article and get random revision.
        if processing:
            index = 1935
        else:
            index = randint(0,2023)
        line = 0
        with open("../articles/CRISPR_" + LANGUAGE) as article:
            while line < index:
                article.readline()
                line += 1
            revision = Revision(**loads(article.readline()))

        file.write("You are looking at revision number " + str(index) + " from " + Timestamp(revision.timestamp).string + "." + "\n")
        #URL of revsions
        heading("\nURL OF REVISION", file)
        file.write(revision.url + "\n")

        #Print text from html
        heading("\nTEXT", file)
        
        start = datetime.now()
        if processing == "_raw":
            #RAW TEXT
            file.write(revision.get_text().strip() + "\n")
        if processing == "_preprocessor":
            #TOKENIZED USING PREPROCESSOR
            from preprocessor.preprocessor import Preprocessor
            preprocessor = Preprocessor("en")
            file.write("|".join(preprocessor.preprocess(revision.get_text().strip() + "\n", lower=False, stopping=False, sentenize=False, tokenize=True)[0]))
        if processing == "_spacy":
            #TOKENIZED USING SPACY
            from spacy import load
            from spacy.lang.en import English
            spacy = English()
            file.write("|".join([str(token) for token in spacy(revision.get_text().strip() + "\n")]))
        print(datetime.now() - start)

        if not processing:

            #Print paragraphs from html
            heading("\nPARAGRAPHS", file)
            paragraphs = revision.get_paragraphs()
            file.write(sub(r"\n\n+", "\n\n", "\n\n".join([section.text() for section in paragraphs])) + "\n")

            #Print headings from html
            heading("\nHEADINGS", file)
            headings = revision.get_headings()
            file.write(sub(r"\n\n+", "\n\n", "\n\n".join([section.text() for section in headings])) + "\n")

            #Print lists from html
            heading("\nLISTS", file)
            lists = revision.get_lists()
            file.write(sub(r"\n\n+", "\n\n", "\n\n".join([section.text() for section in lists])) + "\n")

            #Print captions from html
            heading("\nCAPTIONS", file)
            captions = revision.get_captions()
            file.write(sub(r"\n\n+", "\n\n", "\n\n".join([section.text() for section in captions])) + "\n")

            #Print tables from html
            heading("\nTABLES", file)
            tables = revision.get_tables()
            file.write(sub(r"\n\n+", "\n\n", "\n\n".join([section.text() for section in tables])) + "\n")

            #Print all categories.
            heading("\nCATEGORIES", file)
            for category in revision.get_categories():
                file.write(str(category) + "\n")
            
            #Print references and further reading from html.
            CITATION_STYLE = LANGUAGE #citation style different for German (de) and English (en)
            sources = {"REFERENCES": revision.get_references(), "FURTHER READING":revision.get_further_reading()}
            sections = paragraphs + headings + lists + captions + tables
            for source in sources.items():
                authors = revision.get_referenced_authors(CITATION_STYLE, source[1])
                titles = revision.get_referenced_titles(CITATION_STYLE, source[1])
                dois = revision.get_referenced_dois(source[1])
                heading("\n" + source[0] + " " + "(" + str(len(source[1])) + ")", file)
                for reference, author, title, doi in zip(source[1], authors, titles, dois):
                    file.write("NUMBER: " + str(reference.number) + "\n")
                    file.write("REFERENCE TEXT: " + reference.text().strip() + "\n")
                    file.write("\n")
                    file.write("AUTHORS: " + str(author) + "\n")
                    file.write("TITLE: " + str(title) + "\n")
                    file.write("DOIS: " + str(doi) + "\n")
                    file.write("\nLINKED PARAGRAPHS:" + "\n")
                    backlinks = reference.backlinks()
                    if backlinks:
                        file.write("\n".join(["=>" + str(backlink) + "\n" + linked_section.text().strip() for backlink, linked_section in zip(backlinks, reference.linked_sections(sections))]) + "\n")
                    else:
                        file.write("-" + "\n")
                    file.write("-"*50 + "\n")
