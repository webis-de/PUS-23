from article.article import Article
from timeline.eventlist import EventList
from timeline.accountlist import AccountList
from bibliography.bibliography import Bibliography
from utility.utils import flatten_list_of_lists
from utility.logger import Logger
from preprocessor.preprocessor import Preprocessor
from multiprocessing import Pool
from re import search
from argparse import ArgumentParser
from os.path import sep, exists
from os import makedirs
from re import split
from json import load, dump
from urllib.parse import quote, unquote

##################################################################
# This file serves as an entry point to test the entire pipeline.#
##################################################################

def occurrence(revision, found = None, total = None):
    if found and total:
        return {"index":str(revision.index),"url":revision.url,"timestamp":revision.timestamp.string,"score":round(len(found)/len(total), 2)}
    else:
        return {"index":str(revision.index),"url":revision.url,"timestamp":revision.timestamp.string}

def list_to_key(values):
    return "|".join(values)

def list_intersection(list1, list2):
    return "|".join(sorted(set(list1).intersection(set(list2))))

def process(data):
    event = data[0]
    text = data[1]
    words_in_text = data[2]
    sections = data[3]
    referenced_titles = data[4]
    referenced_pmids = data[5]
    referenced_authors = data[6]
    revision = data[7]
    preprocessor = data[8]

    #FIND EVENT AUTHORS (PER BIBKEY)
    for event_bibkey in event.authors:
        event_authors_in_references = [author for author in event.authors[event_bibkey] if author in referenced_authors]
        event_authors_in_references_as_key = list_to_key(event_authors_in_references)
        if event_authors_in_references:
            if event_bibkey not in event.first_occurrence["authors"]:
                event.first_occurrence["authors"][event_bibkey] = {}
            if event_authors_in_references_as_key not in event.first_occurrence["authors"][event_bibkey]:
                event.first_occurrence["authors"][event_bibkey][event_authors_in_references_as_key] = occurrence(revision, event_authors_in_references, event.authors[event_bibkey])

    ##############################################################################################

    #FIND EVENT PMIDS
    event_pmids_in_text = [event_pmid for event_pmid in event.pmids if event_pmid in referenced_pmids]
    event_pmids_in_text_as_key = list_to_key(event_pmids_in_text)
    if event_pmids_in_text and event_pmids_in_text_as_key not in event.first_occurrence["pmids"]:
        event.first_occurrence["pmids"][event_pmids_in_text_as_key] = occurrence(revision, event_pmids_in_text, event.pmids)

    ##############################################################################################

    #FIND EVENT DOIS
    event_dois_in_text = [event_doi for event_doi in event.dois if event_doi in text]
    event_dois_in_text_as_key = list_to_key(event_dois_in_text)
    if event_dois_in_text and event_dois_in_text_as_key not in event.first_occurrence["dois"]:
        event.first_occurrence["dois"][event_dois_in_text_as_key] = occurrence(revision, event_dois_in_text, event.dois)

    ##############################################################################################

    #FIND EVENT TITLES
    event_titles_full_in_references = []
    event_titles_processed_in_references = []
    
    for event_title in event.titles:
        
        if event_title.lower() in referenced_titles:
            event_titles_full_in_references.append(event_title)
        
        #lower, stop and tokenize event title
        preprocessed_event_title = preprocessor.preprocess(event_title, lower=True, stopping=True, sentenize=False, tokenize=True)[0]
        
        for referenced_title in referenced_titles:
            #lower, stop and tokenize referenced title
            preprocessed_referenced_title = preprocessor.preprocess(referenced_title, lower=True, stopping=True, sentenize=False, tokenize=True)[0]
            #calculate number of matching content words
            match_count = sum([1 if word in preprocessed_referenced_title else 0 for word in preprocessed_event_title])
            #add revision if processed event title is partially referenced
            if match_count >= len(preprocessed_event_title) * 0.8:
                event_titles_processed_in_references.append(event_title)
                break

    if event_titles_full_in_references:
        event_titles_full_in_references_as_key = list_to_key(event_titles_full_in_references)
        if event_titles_full_in_references_as_key not in event.first_occurrence["titles"]["full"]:
                event.first_occurrence["titles"]["full"][event_titles_full_in_references_as_key] = occurrence(revision, event_titles_full_in_references, event.titles)
    if event_titles_processed_in_references:
        event_titles_processed_in_references_as_key = list_to_key(event_titles_processed_in_references)
        if event_titles_processed_in_references_as_key not in event.first_occurrence["titles"]["processed"]:
                event.first_occurrence["titles"]["processed"][event_titles_processed_in_references_as_key] = occurrence(revision, event_titles_processed_in_references, event.titles)

    ##############################################################################################

    #FIND EVENT KEYWORDS AND KEYPHRASES
    keywords_and_keyphrases = set(event.keywords)
    keywords = set([keyword for keyword in keywords_and_keyphrases if " " not in keyword])
    keyphrases = set([keyphrase for keyphrase in keywords_and_keyphrases if " " in keyphrase])
    keyword_intersection = keywords.intersection(words_in_text)
    keyphrase_intersection = set([keyphrase for keyphrase in keyphrases if keyphrase.lower() in text.lower()])
    keywords_and_keyphrases_in_text = sorted(keyword_intersection.union(keyphrase_intersection))
    keywords_and_keyphrases_in_text_as_key = "|".join(keywords_and_keyphrases_in_text)
    if keywords_and_keyphrases_in_text and keywords_and_keyphrases_in_text_as_key not in event.first_occurrence["keywords"]:
        event.first_occurrence["keywords"][keywords_and_keyphrases_in_text_as_key] = occurrence(revision, keywords_and_keyphrases_in_text, keywords_and_keyphrases)
    return event

if __name__ == "__main__":

    argument_parser = ArgumentParser()

    argument_parser.add_argument("-i", "--input_dir",
                                 default="../articles",
                                 help="The relative or absolute path to the directory where the articles reside.")
    argument_parser.add_argument("-o", "--output_dir",
                                 default="../analysis",
                                 help="The relative or absolute path to the directory the analysis will be saved.")
    argument_parser.add_argument("-a", "--articles",
                                 default="../data/articles_arno.json",
                                 help="Either the relative of abolute path to a JSON file of articles " + \
                                      "or quoted string of comma-separated articles, " + \
                                      "e.g. 'Cas9,The CRISPR JOURNAL'.")
    argument_parser.add_argument("-l", "--language",
                                 default="en",
                                 help="en or de, defaults to en.")

    args = vars(argument_parser.parse_args())

    input_directory = args["input_dir"]
    output_directory = args["output_dir"]

    logger = Logger(output_directory)

    output_directory = logger.directory
    
    if not exists(output_directory):
        makedirs(output_directory)
    ARTICLES = args["articles"]
    try:
        with open(ARTICLES) as file:
            wikipedia_articles = flatten_list_of_lists(load(file).values())
    except FileNotFoundError:
        wikipedia_articles = [article.strip() for article in split(" *, *", ARTICLES)]
    language = args["language"]

    bibliography = Bibliography("../data/tracing-innovations-lit.bib")
    accountlist = AccountList("../data/CRISPR_events - accounts.csv")

    logger.start("Analysing articles " + ", ".join(wikipedia_articles))

    preprocessor = Preprocessor(language)

    for wikipedia_article in wikipedia_articles:

        logger.start_check(wikipedia_article)
        
        filename = quote(wikipedia_article.replace(" ","_"), safe="")
        filepath = input_directory + sep + filename + "_" + language
        if not exists(filepath):
            logger.end_check(filepath + " does not exist.")
            continue            
        article = Article(filepath)

        revisions = article.yield_revisions()

        revision = next(revisions, None)

        eventlist = EventList("../data/CRISPR_events - events.csv", bibliography, accountlist)
        
        while revision:
            
            print(revision.index)

            ### The full text of the article.
            text = revision.get_text()
            ### All words in the article
            words_in_text = set(preprocessor.preprocess(text, lower=False, stopping=True, sentenize=False, tokenize=True)[0])
            ### All sentences/paragraphs and captions in the article.
            #sections = preprocessor.preprocess(text, lower=True, stopping=False, sentenize=True, tokenize=False)
            sections = [section.text() for section in (revision.get_paragraphs() + revision.get_captions())]
            ### All 'References' and 'Further Reading' elements.
            references_and_further_reading = revision.get_references() + revision.get_further_reading()
            ### All titles occuring in 'References' and 'Further Reading'.
            referenced_titles = set([title.lower() for title in revision.get_referenced_titles(language, references_and_further_reading)])
            ### All PMIDs occuring in 'References' and 'Further Reading'.
            referenced_pmids = set(flatten_list_of_lists(revision.get_referenced_pmids(references_and_further_reading)))
            ### All authors occuring in 'References' and 'Further Reading'.
            referenced_authors = set([author[0] for author in flatten_list_of_lists(revision.get_referenced_authors(language, references_and_further_reading))])
            
            with Pool(10) as pool:
                eventlist.events = pool.map(process, [(event, text, words_in_text, sections, referenced_titles, referenced_pmids, referenced_authors, revision, preprocessor) for event in eventlist.events])
                         
            revision = next(revisions, None)

        logger.end_check("Done.")

        for i in range(len(eventlist.events)):
            for doi in eventlist.events[i].first_occurrence["authors"]:
                eventlist.events[i].first_occurrence["authors"][doi] = {k:v for k,v in sorted(eventlist.events[i].first_occurrence["authors"][doi].items(), key=lambda item: item[1]["score"], reverse=True)}
            eventlist.events[i].first_occurrence["dois"] = {k:v for k,v in sorted(eventlist.events[i].first_occurrence["dois"].items(), key=lambda item: item[1]["score"], reverse=True)}
            eventlist.events[i].first_occurrence["pmids"] = {k:v for k,v in sorted(eventlist.events[i].first_occurrence["pmids"].items(), key=lambda item: item[1]["score"], reverse=True)}
            for method in eventlist.events[i].first_occurrence["titles"]:
                eventlist.events[i].first_occurrence["titles"][method] = {k:v for k,v in sorted(eventlist.events[i].first_occurrence["titles"][method].items(), key=lambda item: item[1]["score"], reverse=True)}
            eventlist.events[i].first_occurrence["keywords"] = {k:v for k,v in sorted(eventlist.events[i].first_occurrence["keywords"].items(), key=lambda item: item[1]["score"], reverse=True)}

        with open(output_directory + sep + filename + "_" + language + "." + "txt", "w") as file:
            file.write(("\n"+"-"*50+"\n").join([str(event) for event in eventlist.events]))
        with open(output_directory + sep + filename + "_" + language + "." + "json", "w") as file:
            for event in eventlist.events:
                dump(event.json(), file)
                file.write("\n")

    logger.close()
