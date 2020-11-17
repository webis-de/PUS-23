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

#####################################################################
# This file serves as an entry point to test the article extraction.#
#####################################################################

def occurrence(revision, result = False, mean = False, found = None, total = None):
    if result:
        return {"index":revision.index,"url":revision.url,"timestamp":revision.timestamp.string,"result":result,"mean":round(mean, 5)}
    elif found and total:
        return {"index":revision.index,"url":revision.url,"timestamp":revision.timestamp.string,"share":round(len(found)/len(total), 2)}
    else:
        return {"index":revision.index,"url":revision.url,"timestamp":revision.timestamp.string}

def concatenate_list(values):
    return "|".join(values)

def first_or_none(dictionary):
    try:
        return list(dictionary.values())[0]
    except:
        return None

def scroll_to_url(url, string):
    return url + "#:~:text=" + quote(string)   

def jaccard(list1, list2):
    intersection = set(list1).intersection(set(list2))
    union = set(list1).union(set(list2))
    return len(intersection)/len(union)

def ndcg(gains, iDCG, results):
    DCG = sum([(gains[results[i]])/(i+1) if results[i] in gains else 0 for i in range(len(results))])
    return DCG/iDCG

def analyse(event, revision, revision_text, revision_text_lowered, revision_words, reference_texts, referenced_author_sets, referenced_titles, referenced_titles_lowered, referenced_pmids, preprocessor, language):

    #FIND EVENT TITLES
    
    #FULL TEXT SEARCH
    event_titles_full_in_text = []
    for event_title in event.titles.values():
        if event_title.lower() in revision_text_lowered:
            event_titles_full_in_text.append(event_title)

    if event_titles_full_in_text:
        event_titles_full_in_text_as_key = concatenate_list(event_titles_full_in_text)
        if event_titles_full_in_text_as_key not in event.first_occurrence["titles"]["full"]:
                event.first_occurrence["titles"]["full"][event_titles_full_in_text_as_key] = occurrence(revision, found=event_titles_full_in_text, total=event.titles)

    #RELAXED REFERENCE SEARCH
    event_titles_processed_in_references = {}
    for event_bibkey, event_title in event.titles.items():
        normalised_edit_distance = 1.0
        result = {"reference_text":"n/a","normalised_edit_distance":normalised_edit_distance}
        #lower and tokenize event title
        preprocessed_event_title = preprocessor.preprocess(event_title, lower=True, stopping=False, sentenize=False, tokenize=True)[0]
        for referenced_title, reference_text in zip(referenced_titles, reference_texts):
            #lower and tokenize referenced title
            preprocessed_referenced_title = preprocessor.preprocess(referenced_title, lower=True, stopping=False, sentenize=False, tokenize=True)[0]
            #calculate token-based edit distance ratio
            new_normalised_edit_distance = levenshtein(preprocessed_event_title, preprocessed_referenced_title)/len(preprocessed_event_title)
            #add referenced_title if 
            if new_normalised_edit_distance < normalised_edit_distance:
                normalised_edit_distance = new_normalised_edit_distance
                result = {"reference_text":scroll_to_url(revision.url, reference_text),"normalised_edit_distance":normalised_edit_distance}
        event_titles_processed_in_references[event_bibkey] = result
    
    if event_titles_processed_in_references:
        mean_normalised_edit_distance = sum([item["normalised_edit_distance"] for item in event_titles_processed_in_references.values()])/len(event_titles_processed_in_references)
        if mean_normalised_edit_distance < 0.2:
            event.first_occurrence["titles"]["processed"].append(occurrence(revision, result=event_titles_processed_in_references, mean=mean_normalised_edit_distance))

    ##############################################################################################

    #FIND EVENT AUTHORS (PER BIBKEY)
                
    #FULL TEXT SEARCH
    events_in_text_by_authors = {}
    for event_bibkey in event.authors:
        event_authors = event.authors[event_bibkey]
        event_authors_in_text = [author for author in event_authors if author in revision_words]
        proportion = len(event_authors_in_text)/len(event_authors)
        events_in_text_by_authors[event_bibkey] = {"event_authors":concatenate_list(event_authors),"in_text":concatenate_list(event_authors_in_text),"proportion":proportion}
    
    if events_in_text_by_authors:
        mean_proportion = sum([item["proportion"] for item in events_in_text_by_authors.values()])/len(events_in_text_by_authors)
        event.first_occurrence["authors"]["text"].append(occurrence(revision, result=events_in_text_by_authors, mean=mean_proportion))

    #RELAXED REFERENCE SEARCH
    events_in_text_by_authors_jaccard = {}
    events_in_text_by_authors_ndcg = {}
    for event_bibkey in event.authors:
        event_authors = event.authors[event_bibkey]
        gains = {author:len(event_authors)-event_authors.index(author) for author in event_authors}
        iDCG = ndcg(gains=gains, iDCG=1, results=event_authors)
        
        jaccard_score = 0
        jaccard_result = {"reference_text":"n/a", "jaccard_score":0.0}
        
        ndcg_score = 0
        nDCG_result = {"reference_text":"n/a", "ndcg_score":0.0}
        
        for referenced_authors_subset, reference_text in zip(referenced_author_sets, reference_texts):

            new_jaccard_score = jaccard(event_authors, referenced_authors_subset)
            if new_jaccard_score > jaccard_score:
                jaccard_score = new_jaccard_score
                jaccard_result = {"reference_text":scroll_to_url(revision.url, reference_text), "jaccard_score":jaccard_score}
            
            new_ndcg_score = ndcg(gains, iDCG, referenced_authors_subset)
            if new_ndcg_score > ndcg_score:
                ndcg_score = new_ndcg_score
                nDCG_result = {"reference_text":scroll_to_url(revision.url, reference_text), "ndcg_score":ndcg_score}

        events_in_text_by_authors_jaccard[event_bibkey] = jaccard_result
            
        events_in_text_by_authors_ndcg[event_bibkey] = nDCG_result

    if events_in_text_by_authors_jaccard:
        mean_jaccard_score = sum([item["jaccard_score"] for item in events_in_text_by_authors_jaccard.values()])/len(events_in_text_by_authors_jaccard)
        if mean_jaccard_score > 0.8:
            event.first_occurrence["authors"]["jaccard"].append(occurrence(revision, result=events_in_text_by_authors_jaccard, mean=mean_jaccard_score))
    if events_in_text_by_authors_ndcg:
        mean_ndcg_score = sum([item["ndcg_score"] for item in events_in_text_by_authors_ndcg.values()])/len(events_in_text_by_authors_ndcg)
        if mean_ndcg_score > 0.8:
            event.first_occurrence["authors"]["ndcg"].append(occurrence(revision, result=events_in_text_by_authors_ndcg, mean=mean_ndcg_score))

    ##############################################################################################

    #FIND EVENT PMIDS
    event_pmids_in_references = [event_pmid for event_pmid in event.pmids if event_pmid in referenced_pmids]
    event_pmids_in_references_as_key = concatenate_list(event_pmids_in_references)
    if event_pmids_in_references and event_pmids_in_references_as_key not in event.first_occurrence["pmids"]:
        event.first_occurrence["pmids"][event_pmids_in_references_as_key] = occurrence(revision, found=event_pmids_in_references, total=event.pmids)

    ##############################################################################################

    #FIND EVENT DOIS
    event_dois_in_text = [event_doi for event_doi in event.dois if event_doi.lower() in revision_text_lowered]
    event_dois_in_text_as_key = concatenate_list(event_dois_in_text)
    if event_dois_in_text and event_dois_in_text_as_key not in event.first_occurrence["dois"]:
        event.first_occurrence["dois"][event_dois_in_text_as_key] = occurrence(revision, found=event_dois_in_text, total=event.dois)

    ##############################################################################################

    #FIND EVENT KEYWORDS AND KEYPHRASES
    keywords_and_keyphrases = set(event.keywords)
    #select keywords: no spaces
    keywords = set([keyword for keyword in keywords_and_keyphrases if " " not in keyword])
    #select keyphrases: spaces
    keyphrases = set([keyphrase for keyphrase in keywords_and_keyphrases if " " in keyphrase])
    #intersection of keywords and words in text
    keyword_intersection = keywords.intersection(revision_words)
    #intersection of keyphrases and raw text
    keyphrase_intersection = set([keyphrase for keyphrase in keyphrases if keyphrase.lower() in revision_text_lowered])
    #union of keywords and keyphrases in text
    keywords_and_keyphrases_in_text = sorted(keyword_intersection.union(keyphrase_intersection))
    
    keywords_and_keyphrases_in_text_as_key = concatenate_list(keywords_and_keyphrases_in_text)
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
            revision_text = revision.get_text()
            revision_text_lowered = revision_text.lower()
            ### All words in the article
            revision_words = set(preprocessor.preprocess(revision_text, lower=False, stopping=True, sentenize=False, tokenize=True)[0])
            ### All 'References' and 'Further Reading' elements.
            references_and_further_reading = revision.get_references() + revision.get_further_reading()
            ### All titles occuring in 'References' and 'Further Reading'.
            referenced_titles = [reference.get_title(language) for reference in references_and_further_reading]
            referenced_titles_lowered = [title.lower() for title in referenced_titles]
            ### All PMIDs occuring in 'References' and 'Further Reading'.
            referenced_pmids = set(flatten_list_of_lists([reference.get_pmids() for reference in references_and_further_reading]))
            ### All authors occuring in 'References' and 'Further Reading'.
            referenced_author_sets = [[author[0] for author in reference.get_authors(language)] for reference in references_and_further_reading]
            ### All reference texts
            reference_texts = [reference.get_text().strip() for reference in references_and_further_reading]
            with Pool(10) as pool:
                eventlist.events = pool.starmap(analyse,
                                                [(event,
                                                  revision,
                                                  revision_text,
                                                  revision_text_lowered,
                                                  revision_words,
                                                  reference_texts,
                                                  referenced_author_sets,
                                                  referenced_titles,
                                                  referenced_titles_lowered,
                                                  referenced_pmids,
                                                  preprocessor,
                                                  language)
                                                 for event in eventlist.events])
                         
            revision = next(revisions, None)

        logger.end_check("Done.")

        for i in range(len(eventlist.events)):
            eventlist.events[i].first_occurrence["titles"]["full"] = first_or_none({k:v for k,v in sorted(eventlist.events[i].first_occurrence["titles"]["full"].items(), key=lambda item: item[1]["share"], reverse=True)})
            eventlist.events[i].first_occurrence["titles"]["processed"] = first_or_none({r[0]+1:r[1] for r in enumerate(eventlist.events[i].first_occurrence["titles"]["processed"][:5])})
            for metric in ["text", "jaccard", "ndcg"]:
                eventlist.events[i].first_occurrence["authors"][metric] = first_or_none({r[0]+1:r[1] for r in enumerate(eventlist.events[i].first_occurrence["authors"][metric][:5])})
            eventlist.events[i].first_occurrence["dois"] = {k:v for k,v in sorted(eventlist.events[i].first_occurrence["dois"].items(), key=lambda item: item[1]["share"], reverse=True)}
            eventlist.events[i].first_occurrence["pmids"] = {k:v for k,v in sorted(eventlist.events[i].first_occurrence["pmids"].items(), key=lambda item: item[1]["share"], reverse=True)}
            eventlist.events[i].first_occurrence["keywords"] = {k:v for k,v in sorted(eventlist.events[i].first_occurrence["keywords"].items(), key=lambda item: item[1]["share"], reverse=True)}

        with open(output_directory + sep + filename + "_" + language + "." + "txt", "w") as file:
            file.write(("\n"+"-"*50+"\n").join([str(event) for event in eventlist.events]))
        with open(output_directory + sep + filename + "_" + language + "." + "json", "w") as file:
            file.write("[\n")
            first_line = True
            for event in eventlist.events:
                if not first_line:
                    file.write(",\n")
                else:
                    first_line = False
                dump(event.json(), file)
            file.write("\n]")

    logger.close()
