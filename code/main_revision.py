from article.article import Article
from preprocessor.preprocessor import Preprocessor
from random import randint
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

    #SELECT PROCESSING
    PROCESSING = ["", "_raw", "_preprocessor"][0]
    #SELECT LANGUAGE
    LANGUAGE = ["en", "de"][0]
    #SELECT REVISION FILE
    FILEPATH = "../articles/2021-03-01/CRISPR_" + LANGUAGE
    #SELECT REVID
    REVID = None
    #SELECT INDEX
    INDEX = 1589 #randint(0, len(open(FILEPATH).readlines()) - 1)

    preprocessor = Preprocessor(LANGUAGE, ["prokaryotic antiviral system", "10.\d{4,9}/[-\._;\(\)/:a-zA-Z0-9]+"])

    with open("revision_extraction" + PROCESSING + ".txt", "w", encoding="utf-8") as file:        
        revision = Article(FILEPATH).get_revision(INDEX, REVID)
        index = revision.index
        
        preprocessing_start = datetime.now()
        if PROCESSING == "_raw" or PROCESSING == "":
            #RAW TEXT WITHOUT TOKENIZATION
            TEXT = revision.get_text().strip() + "\n"
        if PROCESSING == "_preprocessor":
            #TOKENIZED USING PREPROCESSOR
            TEXT = "|".join(preprocessor.preprocess(revision.get_text().strip() + "\n", lower=False, stopping=False, sentenize=False, tokenize=True)[0])
        preprocessing_end = datetime.now()
        print("Preprocessing: ", preprocessing_end - preprocessing_start)

        extraction_start = datetime.now()

        file.write("You are looking at revision number " + str(index) + " from " + revision.timestamp.string + "." + "\n")
        #URL of revision
        heading("\nURL OF REVISION", file)
        file.write(revision.url + "\n")

        #text from html
        heading("\nTEXT", file)
        if PROCESSING: file.write("Processing text took : " + str(preprocessing_end - preprocessing_start) + "\n\n")

        file.write(TEXT)

        if not PROCESSING:

            #All sections from html
            section_tree = revision.section_tree()

            #Print paragraphs from html
            heading("\nPARAGRAPHS", file)
            paragraphs = section_tree.get_paragraphs()
            file.write(sub(r"\n\n+", "\n\n", "\n\n".join([paragraph.xpath("string()") for paragraph in paragraphs])) + "\n")

            #Print headings from html
            heading("\nHEADINGS", file)
            headings = section_tree.get_headings()
            file.write(sub(r"\n\n+", "\n\n", "\n\n".join([heading.xpath("string()") for heading in headings])) + "\n")

            #Print lists from html
            heading("\nLISTS", file)
            lists = section_tree.get_lists()
            file.write(sub(r"\n+", "\n", "\n".join([uolist.xpath("string()") for uolist in lists])) + "\n\n")
            
            #Print tables from html
            heading("\nTABLES", file)
            tables = section_tree.get_tables()
            file.write(sub(r"\n+", "\n", "\n".join([table.xpath("string()")  for table in tables])) + "\n\n")

            #Print captions from html
            heading("\nCAPTIONS", file)
            captions = section_tree.get_captions()
            file.write(sub(r"\n\n+", "\n\n", "\n\n".join([caption.xpath("string()") for caption in captions])) + "\n")

            #Print all categories.
            heading("\nCATEGORIES", file)
            for category in revision.get_categories():
                file.write(str(category) + "\n")

            #Print all references in History section.
            heading("\nREFERENCES IN HISTORY SECTION", file)
            history_section_tree = section_tree.find("History")[0]
            for source in history_section_tree.get_sources(revision.get_references()):
                file.write(source.get_text() + "\n")
            
            #Print references and further reading from html.
            CITATION_STYLE = LANGUAGE #citation style different for German (de) and English (en)
            sources = {"REFERENCES": revision.get_references(), "FURTHER READING":revision.get_further_reading()}
            for source in sources.items():
                heading("\n" + source[0] + " " + "(" + str(len(source[1])) + ")", file)
                for reference in source[1]:
                    #file.write("HTML: " + html.tostring(reference.html).decode("utf-8") + "\n")
                    file.write("REFERENCE TEXT: " + \
                               reference.get_text().strip() + "\n")
                    #file.write("REFERENCE TEXT TOKENISED: " + "|".join(preprocessor.preprocess(reference.get_text().strip(), lower=False, stopping=False, sentenize=False, tokenize=True)[0]) + "\n")
                    file.write("\n")
                    file.write("AUTHORS: " + str(reference.get_authors(LANGUAGE)) + "\n")
                    file.write("TITLE: " + str(reference.get_title(LANGUAGE)) + "\n")
                    file.write("DOIs: " + str(reference.get_dois()) + "\n")
                    file.write("PMIDs: " + str(reference.get_pmids()) + "\n")
                    file.write("PMCs: " + str(reference.get_pmcs()) + "\n")
                    file.write("IDENTIFIERS: " + str(reference.get_identifiers()) + "\n")
                    file.write("-"*50 + "\n")
    extraction_end = datetime.now()
    print("Extraction: ", extraction_end - extraction_start)
