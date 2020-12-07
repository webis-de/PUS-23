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

####################################################################
# This file serves as an entry point to analyse Wikipedia articles.#
####################################################################

def occurrence(revision, result):
    return {"index":revision.index,"url":revision.url,"timestamp":revision.timestamp.string,"result":result}

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
    
    #FIND EVENT TITLES
    
    #FULL TEXT SEARCH
    if event.titles and not event.first_mentioned["in_text"]["titles"]:
        event_titles_full_in_text = {event_title:scroll_to_url(revision.url, event_title) for event_title in event.titles.values() if event_title.lower() in revision_text_lowered}
        if len(event_titles_full_in_text) == len(event.titles.values()):
            event.first_mentioned["in_text"]["titles"] = occurrence(revision, result=event_titles_full_in_text)

    #RELAXED REFERENCE SEARCH
    if event.titles and not event.first_mentioned["in_references"]["titles"]:
        event_titles_processed_in_references = {}
        for event_bibkey, event_title in event.titles.items():
            normalised_edit_distance = thresholds["NORMALISED_EDIT_DISTANCE_THRESHOLD"]
            #lower and tokenize event title
            preprocessed_event_title = preprocessor.preprocess(event_title, lower=True, stopping=False, sentenize=False, tokenize=True)[0]
            for referenced_title, reference_text in zip(referenced_titles, reference_texts):
                #lower and tokenize referenced title
                preprocessed_referenced_title = preprocessor.preprocess(referenced_title, lower=True, stopping=False, sentenize=False, tokenize=True)[0]
                #calculate token-based normalised edit distance
                new_normalised_edit_distance = levenshtein(preprocessed_event_title, preprocessed_referenced_title)/len(preprocessed_event_title)
                #update referenced_title if newly calculated normalised edit distance is smaller than old normalised edit distance
                if new_normalised_edit_distance <= normalised_edit_distance:
                    normalised_edit_distance = new_normalised_edit_distance
                    event_titles_processed_in_references[event_bibkey] = {"reference_text":scroll_to_url(revision.url, reference_text),"normalised_edit_distance":normalised_edit_distance}
        
        if len(event_titles_processed_in_references) == len(event.titles):
            event.first_mentioned["in_references"]["titles"] = occurrence(revision, result=event_titles_processed_in_references)

    ##############################################################################################

    #FIND EVENT AUTHORS (PER BIBKEY)
                
    #FULL TEXT SEARCH
    if event.authors and not event.first_mentioned["in_text"]["authors"]:
        revision_words_ascii = [to_ascii(word) for word in revision_words]
        revision_text_ascii = to_ascii(revision_text)
        events_in_text_by_authors = {}
        for event_bibkey in event.authors:
            event_authors = [to_ascii(author) for author in event.authors[event_bibkey]]
            event_authors_in_text = {author:scroll_to_url(revision.url, author) for author in event_authors if (" " not in author and author in revision_words_ascii) or (" " in author and author in revision_text_ascii)}
            author_ratio = len(event_authors_in_text)/len(event_authors)
            if author_ratio >= thresholds["AUTHOR_RATIO_THRESHOLD"]:
                events_in_text_by_authors[event_bibkey] = {"authors":event_authors_in_text,"author_ratio":author_ratio}
        if len(events_in_text_by_authors) == len(event.authors):
            event.first_mentioned["in_text"]["authors"] = occurrence(revision, result=events_in_text_by_authors)

    #RELAXED REFERENCE SEARCH
    if event.authors:
        if not event.first_mentioned["in_references"]["authors"]["raw"] or not event.first_mentioned["in_references"]["authors"]["jaccard"] or not event.first_mentioned["in_references"]["authors"]["ndcg"]:
            events_in_references_by_authors_raw = {}
            events_in_references_by_authors_jaccard = {}
            events_in_references_by_authors_ndcg = {}
            for event_bibkey in event.authors:
                event_authors = [to_ascii(author) for author in event.authors[event_bibkey]]
                gains = {author:len(event_authors)-event_authors.index(author) for author in event_authors}
                iDCG = ndcg(gains=gains, iDCG=1, results=event_authors)

                raw_ratio = thresholds["RAW_RATIO_THRESHOLD"]
                jaccard_score = thresholds["JACCARD_SCORE_THRESHOLD"]
                ndcg_score = thresholds["NDCG_SCORE_THRESHOLD"]
                
                for referenced_author_set, reference_text in zip(referenced_author_sets, reference_texts):

                    new_raw_ratio = raw(event_authors, reference_text)
                    if new_raw_ratio >= raw_ratio:
                        raw_ratio = new_raw_ratio
                        events_in_references_by_authors_raw[event_bibkey] = {"reference_text":scroll_to_url(revision.url, reference_text), "raw_ratio":raw_ratio}                

                    new_jaccard_score = jaccard(event_authors, referenced_author_set)
                    if new_jaccard_score >= jaccard_score:
                        jaccard_score = new_jaccard_score
                        events_in_references_by_authors_jaccard[event_bibkey] = {"reference_text":scroll_to_url(revision.url, reference_text), "jaccard_score":jaccard_score}
                    
                    new_ndcg_score = ndcg(gains, iDCG, referenced_author_set)
                    if new_ndcg_score >= ndcg_score:
                        ndcg_score = new_ndcg_score
                        events_in_references_by_authors_ndcg[event_bibkey] = {"reference_text":scroll_to_url(revision.url, reference_text), "ndcg_score":ndcg_score}
                                        
            if not event.first_mentioned["in_references"]["authors"]["raw"] and len(events_in_references_by_authors_raw) == len(event.authors):
                event.first_mentioned["in_references"]["authors"]["raw"] = occurrence(revision, result=events_in_references_by_authors_raw)
                    
            if not event.first_mentioned["in_references"]["authors"]["jaccard"] and len(events_in_references_by_authors_jaccard) == len(event.authors):
                event.first_mentioned["in_references"]["authors"]["jaccard"] = occurrence(revision, result=events_in_references_by_authors_jaccard)

            if not event.first_mentioned["in_references"]["authors"]["ndcg"] and len(events_in_references_by_authors_ndcg) == len(event.authors):
                event.first_mentioned["in_references"]["authors"]["ndcg"] = occurrence(revision, result=events_in_references_by_authors_ndcg)

    ##############################################################################################

    #FIND EVENT PMIDS
    if event.pmids and not event.first_mentioned["in_references"]["pmids"]:
        event_pmids_in_references = {event_pmid:scroll_to_url(revision.url, event_pmid) for event_pmid in event.pmids if event_pmid in referenced_pmids}
        if len(event_pmids_in_references) == len(event.pmids):
            event.first_mentioned["in_references"]["pmids"] = occurrence(revision, result=event_pmids_in_references)

    ##############################################################################################

    #FIND EVENT DOIS
    if event.dois and not event.first_mentioned["in_text"]["dois"]:
        event_dois_in_text = {event_doi:scroll_to_url(revision.url, event_doi) for event_doi in event.dois if event_doi.lower() in revision_text_lowered}
        if len(event_dois_in_text) == len(event.dois):
            event.first_mentioned["in_text"]["dois"] = occurrence(revision, result=event_dois_in_text)

    ##############################################################################################

    #FIND EVENT KEYWORDS AND KEYPHRASES
    if event.keywords and not event.first_mentioned["in_text"]["keywords"]:
        event_keywords_in_text = {keyword:scroll_to_url(revision.url, keyword) for keyword in event.keywords if (" " not in keyword and keyword in revision_words) or (" " in keyword and keyword.lower() in revision_text_lowered)}
        if len(event_keywords_in_text) == len(event.keywords):
            event.first_mentioned["in_text"]["keywords"] = occurrence(revision, result=event_keywords_in_text)

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

    argument_parser.add_argument("-ned", "--normalised_edit_distance_threshold",
                                 type=int,
                                 default=0.2,
                                 help="Threshold for normalised edit distance for titles in references.")
    argument_parser.add_argument("-art", "--author_ratio_threshold",
                                 type=int,
                                 default=1.0,
                                 help="Threshold for authors_in_text/authors_in_reference ratio.")
    argument_parser.add_argument("-rrt", "--raw_ratio_threshold",
                                 type=int,
                                 default=1.0,
                                 help="Raw ratio threshold for authors in reference.")
    argument_parser.add_argument("-jst", "--jaccard_score_threshold",
                                 type=int,
                                 default=0.8,
                                 help="Jaccard score threshold for authors in reference.")
    argument_parser.add_argument("-nst", "--ndcg_score_threshold",
                                 type=int,
                                 default=0.8,
                                 help="nDCG threshold for authors in reference.")

    args = vars(argument_parser.parse_args())

    input_directory = args["input_dir"]
    output_directory = args["output_dir"]
    thresholds = {"NORMALISED_EDIT_DISTANCE_THRESHOLD":args["normalised_edit_distance_threshold"],
                  "AUTHOR_RATIO_THRESHOLD":args["author_ratio_threshold"],
                  "RAW_RATIO_THRESHOLD":args["raw_ratio_threshold"],
                  "JACCARD_SCORE_THRESHOLD":args["jaccard_score_threshold"],
                  "NDCG_SCORE_THRESHOLD":args["ndcg_score_threshold"]}
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
            sources = revision.get_references() + revision.get_further_reading()
            ### All titles occuring in 'References' and 'Further Reading'.
            referenced_titles = [source.get_title(language) for source in sources]
            ### All PMIDs occuring in 'References' and 'Further Reading'.
            referenced_pmids = set(flatten_list_of_lists([source.get_pmids() for source in sources]))
            ### All authors occuring in 'References' and 'Further Reading'.
            referenced_author_sets = [[to_ascii(author[0]) for author in source.get_authors(language)] for source in sources]
            ### All reference texts
            reference_texts = [source.get_text().strip() for source in sources]
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
