from article.article import Article
from timeline.eventlist import EventList
from timeline.accountlist import AccountList
from bibliography.bibliography import Bibliography
from utility.utils import flatten_list_of_lists, levenshtein
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
from math import log

##################################################################
# This file serves as an entry point to test the entire pipeline.#
##################################################################

def occurrence(revision, found = None, total = None, jacc = False, ndcg = False, lev = False, reference_text = ""):
    if jacc:
        return {"reference_text":reference_text,"index":str(revision.index),"url":revision.url,"timestamp":revision.timestamp.string,"jaccard":round(jacc,5)}
    elif ndcg:
        return {"reference_text":reference_text,"index":str(revision.index),"url":revision.url,"timestamp":revision.timestamp.string,"ndcg":round(ndcg,5)}
    elif lev:
        return {"reference_text":reference_text,"index":str(revision.index),"url":revision.url,"timestamp":revision.timestamp.string,"levenshtein":lev}
    elif found and total:
        return {"index":str(revision.index),"url":revision.url,"timestamp":revision.timestamp.string,"share":round(len(found)/len(total), 2)}
    else:
        return {"index":str(revision.index),"url":revision.url,"timestamp":revision.timestamp.string}

def list_to_key(values):
    return "|".join(values)

def jaccard(list1, list2):
    intersection = set(list1).intersection(set(list2))
    union = set(list1).union(set(list2))
    return len(intersection)/len(union)

def ndcg(gains, iDCG, referenced_authors_subset):
    DCG = sum([(2**gains[referenced_authors_subset[i]]-1)/log(i+2,2) if referenced_authors_subset[i] in gains else 0 for i in range(len(referenced_authors_subset))])
    return DCG/iDCG

def list_intersection(list1, list2):
    return "|".join(sorted(set(list1).intersection(set(list2))))

def analyse(event, text, words_in_text, referenced_authors_subsets, reference_texts, referenced_titles, referenced_pmids, revision, preprocessor, language):

    #FIND EVENT AUTHORS (PER BIBKEY)
    for event_bibkey in event.authors:
        event_authors = event.authors[event_bibkey]
        event_authors_in_text = [author for author in event_authors if author in words_in_text]
        event_authors_in_text_as_key = list_to_key(event_authors_in_text)
        
        if event_authors_in_text:
            if event_bibkey not in event.first_occurrence["authors"]["text"]:
                event.first_occurrence["authors"]["text"][event_bibkey] = {}
            if event_authors_in_text_as_key not in event.first_occurrence["authors"]["text"][event_bibkey]:
                event.first_occurrence["authors"]["text"][event_bibkey][event_authors_in_text_as_key] = occurrence(revision, found=event_authors_in_text, total=event_authors)

        gains = {author:len(event_authors)-event_authors.index(author) for author in event_authors}
        iDCG = sum([(2**gains[event_authors[i]]-1)/log(i+2,2) for i in range(len(event_authors))])
        
        jaccard_score = 0
        JACCARD_REFERENCE_TEXT = ""
        nDCG = 0
        NCDG_REFERENCE_TEXT = ""
        
        for referenced_authors_subset, reference_text in zip(referenced_authors_subsets, reference_texts):

            new_jaccard_score = jaccard(event_authors, referenced_authors_subset)
            if new_jaccard_score > jaccard_score:
                jaccard_score = new_jaccard_score
                JACCARD_REFERENCE_TEXT = reference_text
            
            new_nDCG = ndcg(gains, iDCG, referenced_authors_subset)
            if new_nDCG > nDCG:
                nDCG = new_nDCG
                NCDG_REFERENCE_TEXT = reference_text

        if jaccard_score > 0 and JACCARD_REFERENCE_TEXT not in [result["reference_text"] for result in event.first_occurrence["authors"]["jaccard"].get(event_bibkey, [])]:
            if event_bibkey not in event.first_occurrence["authors"]["jaccard"]:
                event.first_occurrence["authors"]["jaccard"][event_bibkey] = []
            event.first_occurrence["authors"]["jaccard"][event_bibkey].append(occurrence(revision, jacc=jaccard_score, reference_text=JACCARD_REFERENCE_TEXT))
            
        if nDCG > 0 and NCDG_REFERENCE_TEXT not in [result["reference_text"] for result in event.first_occurrence["authors"]["ndcg"].get(event_bibkey, [])]:
            if event_bibkey not in event.first_occurrence["authors"]["ndcg"]:
                event.first_occurrence["authors"]["ndcg"][event_bibkey] = []
            event.first_occurrence["authors"]["ndcg"][event_bibkey].append(occurrence(revision, ndcg=nDCG, reference_text=NCDG_REFERENCE_TEXT))

    ##############################################################################################

    #FIND EVENT PMIDS
    event_pmids_in_references = [event_pmid for event_pmid in event.pmids if event_pmid in referenced_pmids]
    event_pmids_in_references_as_key = list_to_key(event_pmids_in_references)
    if event_pmids_in_references and event_pmids_in_references_as_key not in event.first_occurrence["pmids"]:
        event.first_occurrence["pmids"][event_pmids_in_references_as_key] = occurrence(revision, found=event_pmids_in_references, total=event.pmids)

    ##############################################################################################

    #FIND EVENT DOIS
    event_dois_in_text = [event_doi for event_doi in event.dois if event_doi in text]
    event_dois_in_text_as_key = list_to_key(event_dois_in_text)
    if event_dois_in_text and event_dois_in_text_as_key not in event.first_occurrence["dois"]:
        event.first_occurrence["dois"][event_dois_in_text_as_key] = occurrence(revision, found=event_dois_in_text, total=event.dois)

    ##############################################################################################

    #FIND EVENT TITLES
    event_titles_full_in_references = []
    event_titles_processed_in_references = []
    
    for event_title in event.titles:

        if referenced_titles:
            if event_title.lower() in referenced_titles[1]:
                event_titles_full_in_references.append(event_title)
        
        #lower, stop and tokenize event title
        preprocessed_event_title = preprocessor.preprocess(event_title, lower=True, stopping=False, sentenize=False, tokenize=True)[0]
        for referenced_title, reference_text in zip(referenced_titles, reference_texts):
            #lower, stop and tokenize referenced title
            preprocessed_referenced_title = preprocessor.preprocess(referenced_title[1], lower=True, stopping=False, sentenize=False, tokenize=True)[0]
            #calculate token-based edit distance
            edit_distance_ratio = levenshtein(preprocessed_event_title, preprocessed_referenced_title)/len(preprocessed_event_title)
            #add referenced_title if edit distance to length of event title ratio is less than 0.1
            if edit_distance_ratio < 0.2:
                event_titles_processed_in_references.append((referenced_title[0], reference_text, edit_distance_ratio))
                break

    if event_titles_full_in_references:
        event_titles_full_in_references_as_key = list_to_key(event_titles_full_in_references)
        if event_titles_full_in_references_as_key not in event.first_occurrence["titles"]["full"]:
                event.first_occurrence["titles"]["full"][event_titles_full_in_references_as_key] = occurrence(revision, found=event_titles_full_in_references, total=event.titles)
    if event_titles_processed_in_references:
        event_titles_processed_in_references_as_key = list_to_key([item[0] for item in event_titles_processed_in_references])
        reference_texts_of_processed_event_titles_in_references = [item[1] for item in event_titles_processed_in_references]
        edit_distance_ratios_of_processed_event_titles_in_references = [item[2] for item in event_titles_processed_in_references]
        if event_titles_processed_in_references_as_key not in event.first_occurrence["titles"]["processed"]:
                event.first_occurrence["titles"]["processed"][event_titles_processed_in_references_as_key] = occurrence(revision,
                                                                                                                        reference_text=reference_texts_of_processed_event_titles_in_references,
                                                                                                                        lev=edit_distance_ratios_of_processed_event_titles_in_references)

    ##############################################################################################

    #FIND EVENT KEYWORDS AND KEYPHRASES
    keywords_and_keyphrases = set(event.keywords)
    #select keywords: no spaces
    keywords = set([keyword for keyword in keywords_and_keyphrases if " " not in keyword])
    #select keyphrases: spaces
    keyphrases = set([keyphrase for keyphrase in keywords_and_keyphrases if " " in keyphrase])
    #intersection of keywords and words in text
    keyword_intersection = keywords.intersection(words_in_text)
    #intersection of keyphrases and raw text
    keyphrase_intersection = set([keyphrase for keyphrase in keyphrases if keyphrase.lower() in text.lower()])
    #union of keywords and keyphrases in text
    keywords_and_keyphrases_in_text = sorted(keyword_intersection.union(keyphrase_intersection))
    
    keywords_and_keyphrases_in_text_as_key = list_to_key(keywords_and_keyphrases_in_text)
    if keywords_and_keyphrases_in_text and keywords_and_keyphrases_in_text_as_key not in event.first_occurrence["keywords"]:
        event.first_occurrence["keywords"][keywords_and_keyphrases_in_text_as_key] = occurrence(revision, found=keywords_and_keyphrases_in_text, total=keywords_and_keyphrases)
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
            #sections = [section.text() for section in (revision.get_paragraphs() + revision.get_captions())]
            #sections = []
            ### All 'References' and 'Further Reading' elements.
            references_and_further_reading = revision.get_references() + revision.get_further_reading()
            ### All titles occuring in 'References' and 'Further Reading'.
            referenced_titles = [(title, title.lower()) for title in [reference.get_title(language) for reference in references_and_further_reading]]
            ### All PMIDs occuring in 'References' and 'Further Reading'.
            referenced_pmids = set(flatten_list_of_lists([reference.get_pmids() for reference in references_and_further_reading]))
            ### All authors occuring in 'References' and 'Further Reading'.
            referenced_authors_subsets = [[author[0] for author in reference.get_authors(language)] for reference in references_and_further_reading]
            ### All reference texts
            reference_texts = [reference.text().replace("\n","") for reference in references_and_further_reading]
            with Pool(10) as pool:
                eventlist.events = pool.starmap(analyse,
                                                [(event, text, words_in_text, referenced_authors_subsets, reference_texts, referenced_titles, referenced_pmids, revision, preprocessor, language)
                                                 for event in eventlist.events])
                         
            revision = next(revisions, None)

        logger.end_check("Done.")

        for i in range(len(eventlist.events)):
            for bibkey in eventlist.events[i].first_occurrence["authors"]["text"]:
                eventlist.events[i].first_occurrence["authors"]["text"][bibkey] = {k:v for k,v in sorted(eventlist.events[i].first_occurrence["authors"]["text"][bibkey].items(), key=lambda item: item[1]["share"], reverse=True)}
            for bibkey in eventlist.events[i].first_occurrence["authors"]["jaccard"]:
                eventlist.events[i].first_occurrence["authors"]["jaccard"][bibkey] = sorted(eventlist.events[i].first_occurrence["authors"]["jaccard"][bibkey], key=lambda x: x["jaccard"], reverse=True)[:5]
            for bibkey in eventlist.events[i].first_occurrence["authors"]["ndcg"]:
                eventlist.events[i].first_occurrence["authors"]["ndcg"][bibkey] = sorted(eventlist.events[i].first_occurrence["authors"]["ndcg"][bibkey], key=lambda x: x["ndcg"], reverse=True)[:5]
            eventlist.events[i].first_occurrence["dois"] = {k:v for k,v in sorted(eventlist.events[i].first_occurrence["dois"].items(), key=lambda item: item[1]["share"], reverse=True)}
            eventlist.events[i].first_occurrence["pmids"] = {k:v for k,v in sorted(eventlist.events[i].first_occurrence["pmids"].items(), key=lambda item: item[1]["share"], reverse=True)}
            eventlist.events[i].first_occurrence["titles"]["full"] = {k:v for k,v in sorted(eventlist.events[i].first_occurrence["titles"]["full"].items(), key=lambda item: item[1]["share"], reverse=True)}
            eventlist.events[i].first_occurrence["titles"]["processed"] = {k:v for k,v in sorted(eventlist.events[i].first_occurrence["titles"]["processed"].items(), key=lambda item: sum(item[1]["levenshtein"])/len(item[1]["levenshtein"]), reverse=True)}
            eventlist.events[i].first_occurrence["keywords"] = {k:v for k,v in sorted(eventlist.events[i].first_occurrence["keywords"].items(), key=lambda item: item[1]["share"], reverse=True)}

        with open(output_directory + sep + filename + "_" + language + "." + "txt", "w") as file:
            file.write(("\n"+"-"*50+"\n").join([str(event) for event in eventlist.events]))
        with open(output_directory + sep + filename + "_" + language + "." + "json", "w") as file:
            for event in eventlist.events:
                dump(event.json(), file)
                file.write("\n")

    logger.close()
