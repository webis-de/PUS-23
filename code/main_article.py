from article.article import Article
from timeline.eventlist import EventList
from timeline.accountlist import AccountList
from bibliography.bibliography import Bibliography
from utility.utils import flatten_list_of_lists, levenshtein
from utility.logger import Logger
from preprocessor.preprocessor import Preprocessor
from multiprocessing import Pool
import unicodedata
from re import search, split
from argparse import ArgumentParser
from os.path import sep, exists
from os import makedirs
from json import load, dumps
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

def exact_match(event_authors, source_text):
    return len([event_author for event_author in event_authors if event_author in source_text])/len(event_authors)

def jaccard(list1, list2):
    intersection = set(list1).intersection(set(list2))
    union = set(list1).union(set(list2))
    return len(intersection)/len(union)

def ndcg(gains, iDCG, results):
    DCG = sum([(gains[results[i]])/(i+1) if results[i] in gains else 0 for i in range(len(results))])
    return DCG/iDCG

def analyse(event, revision, revision_text_ascii_lowered, revision_words_ascii, source_texts, source_texts_ascii, referenced_author_sets_ascii, referenced_titles, referenced_pmids, preprocessor, language, thresholds):

    #FIND EVENT TITLES
    if event.titles:
        #EXACT MATCH SEARCH
        if not event.first_mentioned["titles"]["exact_match"]:
            event_titles_exact = {}
            for event_bibkey, event_title in event.titles.items():
                if to_ascii(event_title.lower()) in revision_text_ascii_lowered:
                    event_titles_exact[event_bibkey] = scroll_to_url(revision.url, event_title)
            if len(event_titles_exact) == len(event.titles.values()):
                event.first_mentioned["titles"]["exact_match"] = occurrence(revision, result=event_titles_exact)
        #RELAXED REFERENCE SEARCH
        if not event.first_mentioned["titles"]["ned"]:
            event_titles_processed = {}
            for event_bibkey, event_title in event.titles.items():
                normalised_edit_distance = thresholds["NORMALISED_EDIT_DISTANCE_THRESHOLD"]
                #lower and tokenize event title
                preprocessed_event_title = preprocessor.preprocess(event_title, lower=True, stopping=False, sentenize=False, tokenize=True)[0]
                for referenced_title, source_text in zip(referenced_titles, source_texts):
                    #lower and tokenize referenced title
                    preprocessed_referenced_title = preprocessor.preprocess(referenced_title, lower=True, stopping=False, sentenize=False, tokenize=True)[0]
                    #calculate token-based normalised edit distance
                    new_normalised_edit_distance = levenshtein(preprocessed_event_title, preprocessed_referenced_title)/len(preprocessed_event_title)
                    #update referenced_title if newly calculated normalised edit distance is smaller than old normalised edit distance
                    if new_normalised_edit_distance <= normalised_edit_distance:
                        normalised_edit_distance = new_normalised_edit_distance
                        event_titles_processed[event_bibkey] = {"source_text":scroll_to_url(revision.url, source_text),"normalised_edit_distance":normalised_edit_distance}

            if len(event_titles_processed) == len(event.titles):
                event.first_mentioned["titles"]["ned"] = occurrence(revision, result=event_titles_processed)

    ##############################################################################################

    #FIND AUTHORS IN REFERENCES
    if event.authors:
        if not event.first_mentioned["authors"]["exact_match"] or not event.first_mentioned["authors"]["jaccard"] or not event.first_mentioned["authors"]["ndcg"]:
            events_in_references_by_authors_exact_match = {}
            events_in_references_by_authors_jaccard = {}
            events_in_references_by_authors_ndcg = {}
            for event_bibkey in event.authors:
                event_authors = [to_ascii(author) for author in event.authors[event_bibkey]]
                gains = {author:len(event_authors)-event_authors.index(author) for author in event_authors}
                iDCG = ndcg(gains=gains, iDCG=1, results=event_authors)

                exact_match_ratio = thresholds["EXACT_MATCH_RATIO_THRESHOLD"]
                jaccard_score = thresholds["JACCARD_SCORE_THRESHOLD"]
                ndcg_score = thresholds["NDCG_SCORE_THRESHOLD"]

                for referenced_author_set_ascii, source_text, source_text_ascii in zip(referenced_author_sets_ascii, source_texts, source_texts_ascii):

                    new_exact_match_ratio = exact_match(event_authors, source_text_ascii)
                    if new_exact_match_ratio >= exact_match_ratio:
                        exact_match_ratio = new_exact_match_ratio
                        events_in_references_by_authors_exact_match[event_bibkey] = {"source_text":scroll_to_url(revision.url, source_text), "exact_match_ratio":exact_match_ratio}                

                    new_jaccard_score = jaccard(event_authors, referenced_author_set_ascii)
                    if new_jaccard_score >= jaccard_score:
                        jaccard_score = new_jaccard_score
                        events_in_references_by_authors_jaccard[event_bibkey] = {"source_text":scroll_to_url(revision.url, source_text), "jaccard_score":jaccard_score}

                    new_ndcg_score = ndcg(gains, iDCG, referenced_author_set_ascii)
                    if new_ndcg_score >= ndcg_score:
                        ndcg_score = new_ndcg_score
                        events_in_references_by_authors_ndcg[event_bibkey] = {"source_text":scroll_to_url(revision.url, source_text), "ndcg_score":ndcg_score}

            if not event.first_mentioned["authors"]["exact_match"] and len(events_in_references_by_authors_exact_match) == len(event.authors):
                event.first_mentioned["authors"]["exact_match"] = occurrence(revision, result=events_in_references_by_authors_exact_match)

            if not event.first_mentioned["authors"]["jaccard"] and len(events_in_references_by_authors_jaccard) == len(event.authors):
                event.first_mentioned["authors"]["jaccard"] = occurrence(revision, result=events_in_references_by_authors_jaccard)

            if not event.first_mentioned["authors"]["ndcg"] and len(events_in_references_by_authors_ndcg) == len(event.authors):
                event.first_mentioned["authors"]["ndcg"] = occurrence(revision, result=events_in_references_by_authors_ndcg)

    ##############################################################################################

    #FIND EVENT DOIS
    if event.dois and not event.first_mentioned["dois"]:
        event_dois_in_text = {event_doi:scroll_to_url(revision.url, event_doi) for event_doi in event.dois if event_doi.lower() in revision_text_ascii_lowered}
        if len(event_dois_in_text) == len(event.dois):
            event.first_mentioned["dois"] = occurrence(revision, result=event_dois_in_text)

    ##############################################################################################

    #FIND EVENT PMIDS
    if event.pmids and not event.first_mentioned["pmids"]:
        event_pmids_in_references = {event_pmid:scroll_to_url(revision.url, event_pmid) for event_pmid in event.pmids if event_pmid in referenced_pmids}
        if len(event_pmids_in_references) == len(event.pmids):
            event.first_mentioned["pmids"] = occurrence(revision, result=event_pmids_in_references)

    ##############################################################################################

    if False:
        #FIND EVENT KEYWORDS AND KEYPHRASES
        if event.keywords and not event.first_mentioned["keywords"]:
            event_keywords_in_text = {keyword:scroll_to_url(revision.url, keyword) for keyword in event.keywords if
                                      (" " not in keyword and keyword in revision_words_ascii) or
                                      (" " in keyword and keyword.lower() in revision_text_ascii_lowered)}
            if len(event_keywords_in_text) == len(event.keywords):
                event.first_mentioned["keywords"] = occurrence(revision, result=event_keywords_in_text)

    return event

if __name__ == "__main__":

    argument_parser = ArgumentParser()

    argument_parser.add_argument("-i", "--input_dir",
                                 default="../articles",
                                 help="The relative or absolute path to the directory where the articles reside.")
    argument_parser.add_argument("-e", "--events",
                                 help="The relative or absolute path to the events CSV.")
    argument_parser.add_argument("-o", "--output_dir",
                                 default="../analysis",
                                 help="The relative or absolute path to the directory the analysis will be saved.")
    argument_parser.add_argument("-a", "--articles",
                                 default="../data/articles_arno.json",
                                 help="Either the relative of abolute path to a JSON file of articles " + \
                                      "or quoted string of comma-separated articles, " + \
                                      "e.g. 'Cas9,The CRISPR JOURNAL'.")
    argument_parser.add_argument("-c", "--conditions",
                                 nargs="+",
                                 default=["event.type=='publication'"],
                                 help="Events to analyse based on conditions provided, defaults to event.type=='publication'.")
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
    argument_parser.add_argument("-emt", "--exact_match_ratio_threshold",
                                 type=int,
                                 default=1.0,
                                 help="Exact_match ratio threshold for authors in reference.")
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
    event_file = args["events"]
    output_directory = args["output_dir"]
    conditions = args["conditions"]
    thresholds = {"NORMALISED_EDIT_DISTANCE_THRESHOLD":args["normalised_edit_distance_threshold"],
                  "AUTHOR_RATIO_THRESHOLD":args["author_ratio_threshold"],
                  "EXACT_MATCH_RATIO_THRESHOLD":args["exact_match_ratio_threshold"],
                  "JACCARD_SCORE_THRESHOLD":args["jaccard_score_threshold"],
                  "NDCG_SCORE_THRESHOLD":args["ndcg_score_threshold"]}
    logger = Logger(output_directory)

    output_directory = logger.directory

    if not exists(output_directory):
        makedirs(output_directory)
    try:
        with open(args["articles"]) as file:
            wikipedia_articles = flatten_list_of_lists(load(file).values())
    except FileNotFoundError:
        wikipedia_articles = [article.strip() for article in split(" *, *", args["articles"])]
    language = args["language"]

    bibliography = Bibliography("../data/tracing-innovations-lit.bib")
    accountlist = AccountList("../data/CRISPR_events - accounts.csv")

    logger.start("Analysing articles [" + ", ".join(wikipedia_articles) + "].")
    logger.log("Using events with conditions:")
    for condition in conditions:
        logger.log(condition)
    logger.log("Using the below thresholds:")
    for threshold in thresholds:
        logger.log(threshold + ": " + str(thresholds[threshold]))

    DOI_REGEX = "10.\d{4,9}/[-\._;\(\)/:a-zA-Z0-9]+"
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

        eventlist = EventList(event_file, bibliography, accountlist)

        selected_events = []
        for event in eventlist.events:
            for condition in conditions:
                if not eval(condition):
                    break
            else:
                if event not in selected_events:
                    selected_events.append(event)
        eventlist.events = selected_events

        while revision:

            print(revision.index)

            #FIX REVISION URL BY REPLACEING SPACES WITH UNDERSCORES
            revision.url = revision.url.replace(" ", "_")

            ### The full text, the lowered full text and all words of the revision. All characters are converted to ASCII.
            revision_text_ascii = to_ascii(revision.get_text())
            revision_text_ascii_lowered = revision_text_ascii.lower()
            revision_words_ascii = None#set(preprocessor.preprocess(revision_text_ascii, lower=False, stopping=True, sentenize=False, tokenize=True)[0])
            ### The sources of the revision, i.e. 'References' and 'Further Reading' elements.
            sources = revision.get_references() + revision.get_further_reading()
            ### The texts of all sources, both full and tokenized.
            source_texts = [source.get_text().strip() for source in sources]
            source_texts_ascii = [to_ascii(source_text) for source_text in source_texts]
            ### All titles occuring in 'References' and 'Further Reading'.
            referenced_titles = [to_ascii(source.get_title(language)) for source in sources]
            ### All PMIDs occuring in 'References' and 'Further Reading'.
            referenced_pmids = set(flatten_list_of_lists([source.get_pmids() for source in sources]))
            ### All authors occuring in 'References' and 'Further Reading'.
            referenced_author_sets_ascii = [[to_ascii(author[0]) for author in source.get_authors(language)] for source in sources]

            with Pool(10) as pool:
                eventlist.events = pool.starmap(analyse,
                                                [(event,
                                                  revision,
                                                  revision_text_ascii_lowered,
                                                  revision_words_ascii,
                                                  source_texts,
                                                  source_texts_ascii,
                                                  referenced_author_sets_ascii,
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
            file.write(",\n".join([dumps(event.json()) for event in eventlist.events]))
            file.write("\n]")

    logger.close()
