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

def occurrence(revision):
    return ["index: " + str(revision.index), "url: " + revision.url, "timestamp: " + revision.timestamp.string]

def keyword_intersection(list1, list2):
    return ", ".join(set(list1).intersection(set(list2)))

def process(data):
    event = data[0]
    text = data[1]
    sections = data[2]
    referenced_titles = data[3]
    referenced_pmids = data[4]
    referenced_authors = data[5]
    occurrence = data[6]
    preprocessor = data[7]

    #iterate over all event dois
    for event_doi in event.dois:
        event_authors_in_references = ", ".join([author for author in event.authors[event_doi] if author in referenced_authors])
        if event_authors_in_references and event_authors_in_references not in event.first_occurrence["authors"][event_doi]:
            event.first_occurrence["authors"][event_doi][event_authors_in_references] = occurrence
##        if event_doi in text:
##            if not event.first_occurrence["dois"][event_doi]:
##                #add revision if event doi is referenced
##                event.first_occurrence["dois"][event_doi] = occurrence
##        else:
##            event_doi_missing = True

        #iterate over all authors of event_doi:
##        for event_author in event.first_occurrence["authors"][event_doi]:
##            if not event.first_occurrence["authors"][event_doi][event_author]:
##                for referenced_author in referenced_authors:
##                    if event_author in referenced_author:
##                        event.first_occurrence["authors"][event_doi][event_author] = occurrence
##                        break

    ##############################################################################################

    event_pmids_in_text = ", ".join([event_pmid for event_pmid in event.pmids if event_pmid in referenced_pmids])
    if event_pmids_in_text and event_pmids_in_text not in event.first_occurrence["pmids"]:
        event.first_occurrence["pmids"][event_pmids_in_text] = occurrence

    ##############################################################################################
                    
    event_dois_in_text = ", ".join([event_doi for event_doi in event.dois if event_doi in text])
    if event_dois_in_text and event_dois_in_text not in event.first_occurrence["dois"]:
        event.first_occurrence["dois"][event_dois_in_text] = occurrence

    ##############################################################################################

    #iterate over all event titles
    event_title_full_missing = False
    event_title_processed_missing = False
    
    for event_title in event.titles:
        
        
        if event_title.lower() in referenced_titles:
            if not event.first_occurrence["titles"][event_title]["full"]:
                #add revision if full event title is referenced
                event.first_occurrence["titles"][event_title]["full"] = occurrence
        else:
            event_title_full_missing = True
        
        #lower, stop and tokenize event title
        preprocessed_event_title = preprocessor.preprocess(event_title, lower=True, stopping=True, sentenize=False, tokenize=True)[0]
        for referenced_title in referenced_titles:
            #lower, stop and tokenize referenced title
            preprocessed_referenced_title = preprocessor.preprocess(referenced_title, lower=True, stopping=True, sentenize=False, tokenize=True)[0]
            match_count = sum([1 if word in preprocessed_referenced_title else 0 for word in preprocessed_event_title])
            #add revision if processed event title is partially referenced
            if match_count >= len(preprocessed_event_title) * 0.8:
                if not event.first_occurrence["titles"][event_title]["processed"]:
                    event.first_occurrence["titles"][event_title]["processed"] = occurrence
                break
        else:
            event_title_processed_missing = True

    if event.titles:
        if not event.first_occurrence["all_titles"]["full"]:
            if not event_title_full_missing:
                event.first_occurrence["all_titles"]["full"] = occurrence

        if not event.first_occurrence["all_titles"]["processed"]:
            if not event_title_processed_missing:
                event.first_occurrence["all_titles"]["processed"] = occurrence

    ##############################################################################################

    #iterate over all event keywords
    words_in_text = preprocessor.preprocess(text, lower=False, stopping=True, sentenize=False, tokenize=True)[0]
    event_keywords_in_text = keyword_intersection(words_in_text, event.keywords)
    if event_keywords_in_text and event_keywords_in_text not in event.first_occurrence["keywords"]:
        event.first_occurrence["keywords"][event_keywords_in_text] = occurrence
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

    preprocessor = Preprocessor(language)

    bibliography = Bibliography("../data/tracing-innovations-lit.bib")
    accountlist = AccountList("../data/CRISPR_events - accounts.csv")

    logger.start("Analysing articles " + ", ".join(wikipedia_articles))

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
            ### Format occurrence
            formatted_occurence = occurrence(revision)
            
            with Pool(10) as pool:
                eventlist.events = pool.map(process, [(event, text, sections, referenced_titles, referenced_pmids, referenced_authors, formatted_occurence, preprocessor) for event in eventlist.events])
                         
            revision = next(revisions, None)

        logger.end_check("Done.")

        with open(output_directory + sep + filename + "_" + language + "." + "txt", "w") as file:
            file.write(("\n"+"-"*50+"\n").join([str(event) for event in eventlist.events]))
        with open(output_directory + sep + filename + "_" + language + "." + "json", "w") as file:
            for event in eventlist.events:
                dump(event.json(), file)
                file.write("\n")

    logger.close()
