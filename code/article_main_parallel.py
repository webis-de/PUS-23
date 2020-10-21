from entity.article import Article
from entity.eventlist import EventList
from entity.accountlist import AccountList
from entity.bibliography import Bibliography
from utility.utils import flatten_list_of_lists
from preprocessor.preprocessor import Preprocessor
from multiprocessing import Pool
from re import search
from datetime import datetime

##################################################################
# This file serves as an entry point to test the entire pipeline.#
##################################################################

def occurrence(revision):
    return ["index: " + str(revision.index), "url: " + revision.url, "timestamp: " + revision.timestamp_pretty_string()]

def process(data):
    event = data[0]
    text = data[1]
    sections = data[2]
    referenced_dois = data[3]
    referenced_titles = data[4]
    occurrence = data[5]

    #iterate over all event dois
    event_doi_missing = False
    for event_doi in event.dois:
        if event_doi in referenced_dois:
            if not event.first_occurrence["dois"][event_doi]:
                #add revision if event doi is referenced
                event.first_occurrence["dois"][event_doi] = occurrence
        else:
            event_doi_missing = True
    if event.dois and not event.first_occurrence["all_dois"]:
        if not event_doi_missing:
            #add revision if all event dois are referenced
            event.first_occurrence["all_dois"] = occurrence

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
    for event_keyword in event.keywords:
        if not event.first_occurrence["keywords"][event_keyword]:
            #add revision if keyword occur in text
            if search(event_keyword, text):
                event.first_occurrence["keywords"][event_keyword] = occurrence

    if event.keywords and not event.first_occurrence["all_keywords"]:
        #iterate over all sections
        for section in sections:
            #iterate over all event keywords
            for event_keyword in event.keywords:
                #break if keyword not in section
                if not search(event_keyword, section):
                    break
            else:
                #add revision if all keywords occur in section
                event.first_occurrence["all_keywords"] = occurrence
                break

    return event
    

if __name__ == "__main__":

    language = "en"
    article = Article("../extractions/CRISPR_" + language)
    bibliography = Bibliography("../data/tracing-innovations-lit.bib")
    accountlist = AccountList("../data/CRISPR_events - accounts.csv")
    eventlist = EventList("../data/CRISPR_events - events.csv", bibliography, accountlist)
    preprocessor = Preprocessor(language)

    revisions = article.yield_revisions()

    revision = next(revisions, None)

    start = datetime.now()
    
    while revision:
        
        print(revision.index)

        ### The full text of the article.
        text = revision.get_text()
        ### All sentences/paragraphs and captions in the article.
        #sections = preprocessor.preprocess(text, lower=True, stopping=False, sentenize=True, tokenize=False)
        sections = [section.text() for section in (revision.get_paragraphs() + revision.get_captions())]
        ### All 'References' and 'Further Reading' elements.
        references_and_further_reading = revision.get_references() + revision.get_further_reading()
        ### All dois occurring in 'References' and 'Further Reading'.
        referenced_dois = set(flatten_list_of_lists(revision.get_referenced_dois(references_and_further_reading)))
        ### All titles occuring in 'References' and 'Further Reading'.
        referenced_titles = set([title.lower() for title in revision.get_referenced_titles("en", references_and_further_reading)])
        ### Format occurrence
        occ = occurrence(revision)
        
        with Pool(4) as pool:
            eventlist.events = pool.map(process, [(event, text, sections, referenced_dois, referenced_titles, occ) for event in eventlist.events])
                     
        revision = next(revisions, None)

    end = datetime.now()

    print(end - start)

    with open("article_extraction.txt", "w") as file:
        file.write(("\n"+"-"*50+"\n").join([str(event) for event in eventlist.events]))
