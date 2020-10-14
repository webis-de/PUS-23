from entity.article import Article
from entity.eventlist import EventList
from entity.bibliography import Bibliography
from preprocessor.preprocessor import Preprocessor

##################################################################
# This file serves as an entry point to test the entire pipeline.#
##################################################################

if __name__ == "__main__":

    language = "de"
    article = Article("../extractions/CRISPR_" + language)
    bibliography = Bibliography("../data/tracing-innovations-lit.bib")
    eventlist = EventList("../data/CRISPR_events - keywords.csv", bibliography)
    preprocessor = Preprocessor(language)

    revisions = article.get_revisions()

    for paragraph in revisions[-1].get_paragraphs():
        print("|".join(preprocessor.preprocess(paragraph.text(), False, False, False, True)[0]) + "\n\n")


    
