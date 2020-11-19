from article.article import Article
from timeline.eventlist import EventList
from timeline.accountlist import AccountList
from bibliography.bibliography import Bibliography
from utility.utils import flatten_list_of_lists, levenshtein
from utility.logger import Logger
from preprocessor.preprocessor import Preprocessor
from multiprocessing import Pool
import unicodedata
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

def occurrence(revision, result = None, mean = None, ratio = None):
    if result is not None and mean is not None:
        return {"index":revision.index,"url":revision.url,"timestamp":revision.timestamp.string,"result":result,"mean":round(mean, 5)}
    elif result is not None and ratio is not None:
        return {"index":revision.index,"url":revision.url,"timestamp":revision.timestamp.string,"result":result,"ratio":round(ratio, 2)}
    else:
        return {"index":revision.index,"url":revision.url,"timestamp":revision.timestamp.string,"ratio":round(ratio, 2)}

def concatenate_list(values):
    return "|".join(values)

def to_ascii(string):
    return unicodedata.normalize("NFD",string).encode("ASCII","ignore").decode("ASCII")

def scroll_to_url(url, string):
    return url + "#:~:text=" + quote(string)

def raw(event_authors, reference_text):
    return len([event_author for event_author in event_authors if event_author in to_ascii(reference_text)])/len(event_authors)

def jaccard(list1, list2):
    intersection = set(list1).intersection(set(list2))
    union = set(list1).union(set(list2))
    return len(intersection)/len(union)

def ndcg(gains, iDCG, results):
    DCG = sum([(gains[results[i]])/(i+1) if results[i] in gains else 0 for i in range(len(results))])
    return DCG/iDCG

def analyse(event, revision, revision_text, revision_text_lowered, revision_words, reference_texts, referenced_author_sets, referenced_titles, referenced_pmids, preprocessor, language, thresholds):

    MEAN_TITLE_RATIO = thresholds["MEAN_TITLE_RATIO"]
    MEAN_NORMALISED_EDIT_DISTANCE = thresholds["MEAN_NORMALISED_EDIT_DISTANCE"]
    MEAN_AUTHOR_RATIO = thresholds["MEAN_AUTHOR_RATIO"]
    MEAN_RAW_RATIO = thresholds["MEAN_RAW_RATIO"]
    MEAN_JACCARD_SCORE = thresholds["MEAN_JACCARD_SCORE"]
    MEAN_NDCG_SCORE = thresholds["MEAN_NDCG_SCORE"]
    
    #FIND EVENT TITLES
    
    #FULL TEXT SEARCH
    if not event.first_occurrence["in_text"]["titles"]:
        event_titles_full_in_text = {event_title:scroll_to_url(revision.url, event_title) for event_title in event.titles.values() if event_title.lower() in revision_text_lowered}
        if event_titles_full_in_text:
            mean_title_ratio = len(event_titles_full_in_text) / len(event.titles.values())
            if mean_title_ratio >= MEAN_TITLE_RATIO:
                    event.first_occurrence["in_text"]["titles"] = occurrence(revision, result=event_titles_full_in_text, ratio=mean_title_ratio)

    #RELAXED REFERENCE SEARCH
    if not event.first_occurrence["in_references"]["titles"]:
        event_titles_processed_in_references = {}
        for event_bibkey, event_title in event.titles.items():
            normalised_edit_distance = 1.0
            titles_result = {"reference_text":"n/a","normalised_edit_distance":normalised_edit_distance}
            #lower and tokenize event title
            preprocessed_event_title = preprocessor.preprocess(event_title, lower=True, stopping=False, sentenize=False, tokenize=True)[0]
            for referenced_title, reference_text in zip(referenced_titles, reference_texts):
                #lower and tokenize referenced title
                preprocessed_referenced_title = preprocessor.preprocess(referenced_title, lower=True, stopping=False, sentenize=False, tokenize=True)[0]
                #calculate token-based normalised edit distance
                new_normalised_edit_distance = levenshtein(preprocessed_event_title, preprocessed_referenced_title)/len(preprocessed_event_title)
                #update referenced_title if newly calculated normalised edit distance is smaller than old normalised edit distance
                if new_normalised_edit_distance < normalised_edit_distance:
                    normalised_edit_distance = new_normalised_edit_distance
                    titles_result = {"reference_text":scroll_to_url(revision.url, reference_text),"normalised_edit_distance":normalised_edit_distance}
            event_titles_processed_in_references[event_bibkey] = titles_result
        
        if event_titles_processed_in_references:
            mean_normalised_edit_distance = sum([item["normalised_edit_distance"] for item in event_titles_processed_in_references.values()])/len(event_titles_processed_in_references)
            if mean_normalised_edit_distance <= MEAN_NORMALISED_EDIT_DISTANCE:
                event.first_occurrence["in_references"]["titles"] = occurrence(revision, result=event_titles_processed_in_references, mean=mean_normalised_edit_distance)

    ##############################################################################################

    #FIND EVENT AUTHORS (PER BIBKEY)
                
    #FULL TEXT SEARCH
    if not event.first_occurrence["in_text"]["authors"]:
        revision_words_ascii = [to_ascii(word) for word in revision_words]
        revision_text_ascii = to_ascii(revision_text)
        events_in_text_by_authors = {}
        for event_bibkey in event.authors:
            event_authors = [to_ascii(author) for author in event.authors[event_bibkey]]
            event_authors_in_text = {author:scroll_to_url(revision.url, author) for author in event_authors if (" " not in author and author in revision_words_ascii) or (" " in author and author in revision_text_ascii)}
            ratio = len(event_authors_in_text)/len(event_authors)
            events_in_text_by_authors[event_bibkey] = {"event_authors":concatenate_list(event.authors[event_bibkey]),"in_text":event_authors_in_text,"ratio":ratio}
        if events_in_text_by_authors:
            mean_author_ratio = sum([item["ratio"] for item in events_in_text_by_authors.values()])/len(events_in_text_by_authors)
            if mean_author_ratio >= MEAN_AUTHOR_RATIO:
                event.first_occurrence["in_text"]["authors"] = occurrence(revision, result=events_in_text_by_authors, mean=mean_author_ratio)

    #RELAXED REFERENCE SEARCH
    if not event.first_occurrence["in_references"]["authors"]["raw"] or not event.first_occurrence["in_references"]["authors"]["jaccard"] or not event.first_occurrence["in_references"]["authors"]["ndcg"]:
        events_in_references_by_authors_raw = {}
        events_in_references_by_authors_jaccard = {}
        events_in_references_by_authors_ndcg = {}
        for event_bibkey in event.authors:
            event_authors = [to_ascii(author) for author in event.authors[event_bibkey]]
            gains = {author:len(event_authors)-event_authors.index(author) for author in event_authors}
            iDCG = ndcg(gains=gains, iDCG=1, results=event_authors)

            raw_score = 0
            raw_result = {"reference_text":"n/a", "raw_score":0.0}
            
            jaccard_score = 0
            jaccard_result = {"reference_text":"n/a", "jaccard_score":0.0}
            
            ndcg_score = 0
            nDCG_result = {"reference_text":"n/a", "ndcg_score":0.0}
            
            for referenced_author_set, reference_text in zip(referenced_author_sets, reference_texts):

                new_raw_score = raw(event_authors, reference_text)
                if new_raw_score > raw_score:
                    raw_score = new_raw_score
                    raw_result = {"reference_text":scroll_to_url(revision.url, reference_text), "raw_score":raw_score}                

                new_jaccard_score = jaccard(event_authors, referenced_author_set)
                if new_jaccard_score > jaccard_score:
                    jaccard_score = new_jaccard_score
                    jaccard_result = {"reference_text":scroll_to_url(revision.url, reference_text), "jaccard_score":jaccard_score}
                
                new_ndcg_score = ndcg(gains, iDCG, referenced_author_set)
                if new_ndcg_score > ndcg_score:
                    ndcg_score = new_ndcg_score
                    nDCG_result = {"reference_text":scroll_to_url(revision.url, reference_text), "ndcg_score":ndcg_score}

            events_in_references_by_authors_raw[event_bibkey] = raw_result
            events_in_references_by_authors_jaccard[event_bibkey] = jaccard_result
            events_in_references_by_authors_ndcg[event_bibkey] = nDCG_result
                                    
        if not event.first_occurrence["in_references"]["authors"]["raw"] and events_in_references_by_authors_raw:
            mean_raw_score = sum([item["raw_score"] for item in events_in_references_by_authors_raw.values()])/len(events_in_references_by_authors_raw)
            if mean_raw_score >= MEAN_RAW_RATIO:
                event.first_occurrence["in_references"]["authors"]["raw"] = occurrence(revision, result=events_in_references_by_authors_raw, mean=mean_raw_score)
                
        if not event.first_occurrence["in_references"]["authors"]["jaccard"] and events_in_references_by_authors_jaccard:
            mean_jaccard_score = sum([item["jaccard_score"] for item in events_in_references_by_authors_jaccard.values()])/len(events_in_references_by_authors_jaccard)
            if mean_jaccard_score >= MEAN_JACCARD_SCORE:
                event.first_occurrence["in_references"]["authors"]["jaccard"] = occurrence(revision, result=events_in_references_by_authors_jaccard, mean=mean_jaccard_score)

        if not event.first_occurrence["in_references"]["authors"]["ndcg"] and events_in_references_by_authors_ndcg:
            mean_ndcg_score = sum([item["ndcg_score"] for item in events_in_references_by_authors_ndcg.values()])/len(events_in_references_by_authors_ndcg)
            if mean_ndcg_score >= MEAN_NDCG_SCORE:
                event.first_occurrence["in_references"]["authors"]["ndcg"] = occurrence(revision, result=events_in_references_by_authors_ndcg, mean=mean_ndcg_score)

    ##############################################################################################

    #FIND EVENT PMIDS
    event_pmids_in_references = [event_pmid for event_pmid in event.pmids if event_pmid in referenced_pmids]
    event_pmids_in_references_as_key = concatenate_list(event_pmids_in_references)
    if event_pmids_in_references and event_pmids_in_references_as_key not in event.first_occurrence["in_references"]["pmids"]:
        pmid_ratio = len(event_pmids_in_references) / len(event.pmids)
        event.first_occurrence["in_references"]["pmids"][event_pmids_in_references_as_key] = occurrence(revision, ratio=pmid_ratio)

    ##############################################################################################

    #FIND EVENT DOIS
    event_dois_in_text = [event_doi for event_doi in event.dois if event_doi.lower() in revision_text_lowered]
    event_dois_in_text_as_key = concatenate_list(event_dois_in_text)
    if event_dois_in_text and event_dois_in_text_as_key not in event.first_occurrence["in_text"]["dois"]:
        doi_ratio = len(event_dois_in_text) / len(event.dois)
        event.first_occurrence["in_text"]["dois"][event_dois_in_text_as_key] = occurrence(revision, ratio=doi_ratio)

    ##############################################################################################

    #FIND EVENT KEYWORDS AND KEYPHRASES
    keywords_in_text = [keyword for keyword in event.keywords if (" " not in keyword and keyword in revision_words) or (" " in keyword and keyword.lower() in revision_text_lowered)]
    keywords_in_text_as_key = concatenate_list(keywords_in_text)
    if keywords_in_text and keywords_in_text_as_key not in event.first_occurrence["keywords"]:
        keyword_ratio = len(keywords_in_text) / len(event.keywords)
        event.first_occurrence["keywords"][keywords_in_text_as_key] = occurrence(revision, ratio=keyword_ratio)

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
    argument_parser.add_argument("-mtp", "--mean_title_ratio",
                                 type=int,
                                 default=1.0,
                                 help="Threshold for titles_in_text/titles_in_bibliography ratio.")
    argument_parser.add_argument("-mned", "--mean_normalised_edit_distance",
                                 type=int,
                                 default=0.2,
                                 help="Threshold for mean normalised edit distance for titles in references.")
    argument_parser.add_argument("-map", "--mean_author_ratio",
                                 type=int,
                                 default=1.0,
                                 help="Threshold for mean authors_in_text/authors_in_reference ratio.")
    argument_parser.add_argument("-mr", "--mean_raw_ratio",
                                 type=int,
                                 default=1.0,
                                 help="Mean raw score threshold.")
    argument_parser.add_argument("-mj", "--mean_jaccard_score",
                                 type=int,
                                 default=0.8,
                                 help="Mean Jaccard score threshold.")
    argument_parser.add_argument("-mndcg", "--mean_ndcg_score",
                                 type=int,
                                 default=0.8,
                                 help="Mean nDCG threshold.")

    args = vars(argument_parser.parse_args())

    input_directory = args["input_dir"]
    output_directory = args["output_dir"]
    thresholds = {"MEAN_TITLE_RATIO":args["mean_title_ratio"],
                  "MEAN_NORMALISED_EDIT_DISTANCE":args["mean_normalised_edit_distance"],
                  "MEAN_AUTHOR_RATIO":args["mean_author_ratio"],
                  "MEAN_RAW_RATIO":args["mean_raw_ratio"],
                  "MEAN_JACCARD_SCORE":args["mean_jaccard_score"],
                  "MEAN_NDCG_SCORE":args["mean_ndcg_score"]}
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
    logger.log("Using the below thresholds:")
    for threshold in thresholds:
        logger.log(threshold + ": " + str(thresholds[threshold]))

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
            ### All PMIDs occuring in 'References' and 'Further Reading'.
            referenced_pmids = set(flatten_list_of_lists([reference.get_pmids() for reference in references_and_further_reading]))
            ### All authors occuring in 'References' and 'Further Reading'.
            referenced_author_sets = [[to_ascii(author[0]) for author in reference.get_authors(language)] for reference in references_and_further_reading]
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
                                                  referenced_pmids,
                                                  preprocessor,
                                                  language,
                                                  thresholds)
                                                 for event in eventlist.events])
                         
            revision = next(revisions, None)

        logger.end_check("Done.")

        for i in range(len(eventlist.events)):
            eventlist.events[i].first_occurrence["in_text"]["dois"] = {k:v for k,v in sorted(eventlist.events[i].first_occurrence["in_text"]["dois"].items(), key=lambda item: item[1]["ratio"], reverse=True)}
            eventlist.events[i].first_occurrence["in_references"]["pmids"] = {k:v for k,v in sorted(eventlist.events[i].first_occurrence["in_references"]["pmids"].items(), key=lambda item: item[1]["ratio"], reverse=True)}
            eventlist.events[i].first_occurrence["keywords"] = {k:v for k,v in sorted(eventlist.events[i].first_occurrence["keywords"].items(), key=lambda item: item[1]["ratio"], reverse=True)}

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
