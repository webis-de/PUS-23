from article.revision.revision import Revision
from preprocessor.preprocessor import Preprocessor
from spacy.lang.en import English
from spacy.lang.de import German
from random import randint
from json import loads
from lxml import html
from re import sub
from datetime import datetime

######################################################################
# This file serves as an entry point to test the Revision extraction.#
######################################################################

def heading(text, file):
    file.write(text + "\n")
    file.write("="*(len(text.replace("\n",""))) + "\n")
    file.write("\n")

if __name__ == "__main__":

    PROCESSING = ["", "_raw", "_preprocessor", "_spacy"][2]
    SELECTION = ["index", "revid", "random"][0]
    LANGUAGE = ["en", "de"][0]
    FILEPATH = "../articles/CRISPR_" + LANGUAGE

    preprocessor = Preprocessor(LANGUAGE, ["prokaryotic antiviral system", "10.\d{4,9}/[-\._;\(\)/:a-zA-Z0-9]+"])
    if LANGUAGE == "en":
        spacy = English()
    if LANGUAGE == "de":
        spacy = German()

    with open("revision_extraction" + PROCESSING + ".txt", "w", encoding="utf-8") as file:        

        #Open scraped article and get random revision.
        if SELECTION == "index":
            #reasonable index for en 1935, for de 100
            index = 1935
            line = 0
            with open(FILEPATH) as article:
                while line < index:
                    article.readline()
                    line += 1
                revision = Revision(**loads(article.readline()))
        elif SELECTION == "revid":
            revid = 648831944
            with open(FILEPATH) as article:
                for line in article:
                    revision = Revision(**loads(line))
                    if revision.revid == 648831944:
                        break
            index = revision.index
        else:
            revision_count = 0
            with open(FILEPATH) as file_to_count:
                for line in file_to_count:
                    revision_count += 1
            index = randint(0, revision_count - 1)
            line = 0
            with open(FILEPATH) as article:
                while line < index:
                    article.readline()
                    line += 1
                revision = Revision(**loads(article.readline()))
        
        preprocessing_start = datetime.now()
        if PROCESSING == "_raw" or PROCESSING == "":
            #RAW TEXT WITHOUT TOKENIZATION
            TEXT = revision.get_text().strip() + "\n"
        if PROCESSING == "_preprocessor":
            #TOKENIZED USING PREPROCESSOR
            TEXT = "|".join(preprocessor.preprocess(revision.get_text().strip() + "\n", lower=False, stopping=False, sentenize=False, tokenize=True)[0])
        if PROCESSING == "_spacy":
            #TOKENIZED USING SPACY
            TEXT = "|".join([str(token) for token in spacy(revision.get_text().strip() + "\n")])
        preprocessing_end = datetime.now()
        print("Preprocessing: ", preprocessing_end - preprocessing_start)

        extraction_start = datetime.now()

        file.write("You are looking at revision number " + str(index) + " from " + revision.timestamp.string + "." + "\n")
        #URL of revsions
        heading("\nURL OF REVISION", file)
        file.write(revision.url + "\n")

        #Print text from html
        heading("\nTEXT", file)
        if PROCESSING: file.write("Processing text took : " + str(preprocessing_end - preprocessing_start) + "\n\n")

        file.write(TEXT)

        if not PROCESSING:

            #Print paragraphs from html
            heading("\nPARAGRAPHS", file)
            paragraphs = revision.get_paragraphs()
            file.write(sub(r"\n\n+", "\n\n", "\n\n".join([section.get_text() for section in paragraphs])) + "\n")

            #Print headings from html
            heading("\nHEADINGS", file)
            headings = revision.get_headings()
            file.write(sub(r"\n\n+", "\n\n", "\n\n".join([section.get_text() for section in headings])) + "\n")

            #Print lists from html
            heading("\nLISTS", file)
            lists = revision.get_lists()
            file.write(sub(r"\n\n+", "\n\n", "\n\n".join([section.get_text() for section in lists])) + "\n")

            #Print captions from html
            heading("\nCAPTIONS", file)
            captions = revision.get_captions()
            file.write(sub(r"\n\n+", "\n\n", "\n\n".join([section.get_text() for section in captions])) + "\n")

            #Print tables from html
            heading("\nTABLES", file)
            tables = revision.get_tables()
            file.write(sub(r"\n\n+", "\n\n", "\n\n".join([section.get_text() for section in tables])) + "\n")

            #Print all categories.
            heading("\nCATEGORIES", file)
            for category in revision.get_categories():
                file.write(str(category) + "\n")
            
            #Print references and further reading from html.
            CITATION_STYLE = LANGUAGE #citation style different for German (de) and English (en)
            sources = {"REFERENCES": revision.get_references(), "FURTHER READING":revision.get_further_reading()}
            sections = paragraphs + headings + lists + captions + tables
            for source in sources.items():
                heading("\n" + source[0] + " " + "(" + str(len(source[1])) + ")", file)
                for reference in source[1]:
                    file.write("SOURCE: " + html.tostring(reference.source).decode("utf-8") + "\n")
                    file.write("NUMBER: " + str(reference.number) + "\n")
                    file.write("REFERENCE TEXT: " + reference.get_text().strip() + "\n")
                    file.write("REFERENCE TEXT TOKENISED: " + "|".join(preprocessor.preprocess(reference.get_text().strip(), lower=False, stopping=False, sentenize=False, tokenize=True)[0]) + "\n")
                    file.write("\n")
                    file.write("AUTHORS: " + str(reference.get_authors(LANGUAGE)) + "\n")
                    file.write("TITLE: " + str(reference.get_title(LANGUAGE)) + "\n")
                    file.write("DOIs: " + str(reference.get_dois()) + "\n")
                    file.write("PMIDs: " + str(reference.get_pmids()) + "\n")
                    file.write("\nLINKED PARAGRAPHS:" + "\n")
                    backlinks = reference.get_backlinks()
                    if backlinks:
                        file.write("\n".join(["=>" + str(backlink) + "\n" + linked_section.get_text().strip() for backlink, linked_section in zip(backlinks, reference.linked_sections(sections))]) + "\n")
                    else:
                        file.write("-" + "\n")
                    file.write("-"*50 + "\n")
    extraction_end = datetime.now()
    print("Extraction: ", extraction_end - extraction_start)
