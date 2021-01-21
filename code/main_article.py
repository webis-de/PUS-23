from article.article import Article
from timeline.eventlist import EventList
from timeline.accountlist import AccountList
from bibliography.bibliography import Bibliography
from utility.utils import flatten_list_of_lists, levenshtein
from utility.logger import Logger
from preprocessor.preprocessor import Preprocessor
from multiprocessing import Pool
from unicodedata import normalize
from re import search, split
from argparse import ArgumentParser
from os.path import basename, exists, sep
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
    return normalize("NFD",string).encode("ASCII","ignore").decode("ASCII")

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

def analyse(event, revision, revision_text_ascii_lowered, source_texts, source_texts_ascii, preprocessed_source_titles_ascii, referenced_author_sets_ascii, referenced_pmids, preprocessor, language, thresholds):

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
                preprocessed_event_title = preprocessor.preprocess(to_ascii(event_title), lower=True, stopping=False, sentenize=False, tokenize=True)[0]
                for preprocessed_source_title_ascii, source_text in zip(preprocessed_source_titles_ascii, source_texts):
                    #calculate token-based normalised edit distance
                    new_normalised_edit_distance = levenshtein(preprocessed_event_title, preprocessed_source_title_ascii)/len(preprocessed_event_title)
                    #update source_title if newly calculated normalised edit distance is smaller than old normalised edit distance
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
            for event_bibkey, event_authors in event.authors.items():
                event_authors = [to_ascii(author) for author in event_authors]
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

    return event

if __name__ == "__main__":

    #Regex for matching DOIS (https://www.crossref.org/blog/dois-and-matching-regular-expressions)
    DOI_REGEX = "10.\d{4,9}/[-\._;\(\)/:a-zA-Z0-9]+"

    argument_parser = ArgumentParser()

    argument_parser.add_argument("-ad", "--articledir",
                                 help="The relative or absolute path to the directory where the articles reside.")
    argument_parser.add_argument("-ef", "--eventfile",
                                 help="The relative or absolute path to the event CSV.")
    argument_parser.add_argument("-od", "--outputdir",
                                 default="../analysis",
                                 help="The relative or absolute path to the directory the analysis will be saved.")
    argument_parser.add_argument("-al", "--articlelist",
                                 nargs="+",
                                 help="The article titles to analyse.")
    argument_parser.add_argument("-af", "--articlefile",
                                 default="../data/articles_arno.json",
                                 help="The file of article titles to analyse.")    
    argument_parser.add_argument("-cond", "--conditions",
                                 nargs="+",
                                 default=[],
                                 help="Conditions according to which events will be filtered.")
    argument_parser.add_argument("-eq", "--equalling",
                                 nargs="+",
                                 default=[],
                                 help="Attributes as strings to which Events will be reduced.")
    argument_parser.add_argument("-lang", "--language",
                                 default="en",
                                 help="en or de, defaults to en.")
    argument_parser.add_argument("-ned", "--normalised_edit_distance_threshold",
                                 type=int,
                                 default=0.2,
                                 help="Threshold for normalised edit distance for titles in references.")
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

    article_directory = args["articledir"]
    event_file = args["eventfile"]
    output_directory = args["outputdir"]
    articles = args["articlelist"]
    conditions = args["conditions"]
    equalling = args["equalling"]
    language = args["language"]
    thresholds = {"NORMALISED_EDIT_DISTANCE_THRESHOLD":args["normalised_edit_distance_threshold"],
                  "EXACT_MATCH_RATIO_THRESHOLD":args["exact_match_ratio_threshold"],
                  "JACCARD_SCORE_THRESHOLD":args["jaccard_score_threshold"],
                  "NDCG_SCORE_THRESHOLD":args["ndcg_score_threshold"]}

    logger = Logger(output_directory)
    output_directory = logger.directory

    if not exists(output_directory): makedirs(output_directory)
    
    if not articles: articles = flatten_list_of_lists(load(open(args["articlefile"])).values())

    bibliography = Bibliography("../data/tracing-innovations-lit.bib")
    accountlist = AccountList("../data/CRISPR_accounts.csv")
    preprocessor = Preprocessor(language)

    logger.start("Analysing articles [" + ", ".join(articles) + "]")
    logger.log("Using event file: " + basename(event_file))

    logger.log("Using events with conditions: " + ", ".join(conditions if conditions else ["-"]))
    logger.log("Equalling events to attributes: " + ", ".join(equalling if equalling else ["-"]))
    logger.log("Using the below thresholds:")
    for threshold in thresholds:
        logger.log(threshold + ": " + str(thresholds[threshold]))    

    for article in articles:

        logger.start_check(article)

        filename = quote(article.replace(" ","_"), safe="")
        filepath = article_directory + sep + filename + "_" + language
        if not exists(filepath):
            logger.end_check(filepath + " does not exist.")
            continue
        
        article = Article(filepath)
        revisions = article.yield_revisions()
        revision = next(revisions, None)

        eventlist = EventList(event_file, bibliography, accountlist, conditions, equalling)

        while revision:

            print(revision.index)

            #FIX REVISION URL BY REPLACEING SPACES WITH UNDERSCORES
            revision.url = revision.url.replace(" ", "_")

            ### The lowered ASCII-normalised full text.
            revision_text_ascii_lowered = to_ascii(revision.get_text()).lower()
            ### The sources of the revision, i.e. 'References' and 'Further Reading' elements.
            sources = revision.get_references() + revision.get_further_reading()
            ### The texts of all sources, both raw and ASCII-normalised.
            source_texts = [source.get_text().strip() for source in sources]
            source_texts_ascii = [to_ascii(source_text) for source_text in source_texts]
            ### All titles occuring in 'References' and 'Further Reading', ASCII-normalised, lowered and tokenised.
            source_titles = [source.get_title(language) for source in sources]
            source_titles_ascii = [to_ascii(source_title) for source_title in source_titles]
            preprocessed_source_titles_ascii = [preprocessor.preprocess(source_title_ascii, lower=True, stopping=False, sentenize=False, tokenize=True)[0] for source_title_ascii in source_titles_ascii]
            ### All authors occuring in 'References' and 'Further Reading', ASCII-normalised.
            referenced_author_sets_ascii = [[to_ascii(author[0]) for author in source.get_authors(language)] for source in sources]
            ### All PMIDs occuring in 'References' and 'Further Reading'.
            referenced_pmids = set(flatten_list_of_lists([source.get_pmids() for source in sources]))

            with Pool(24) as pool:
                eventlist.events = pool.starmap(analyse,
                                                [(event,
                                                  revision,
                                                  revision_text_ascii_lowered,
                                                  source_texts,
                                                  source_texts_ascii,
                                                  preprocessed_source_titles_ascii,
                                                  referenced_author_sets_ascii,
                                                  referenced_pmids,
                                                  preprocessor,
                                                  language,
                                                  thresholds)
                                                 for event in eventlist.events])

            revision = next(revisions, None)

        logger.end_check("Done.")

        eventlist.write_text(output_directory + sep + filename + "_" + language + "." + "txt")
        eventlist.write_json(output_directory + sep + filename + "_" + language + "." + "json")

    logger.close()
