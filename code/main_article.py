from article.article import Article
from timeline.eventlist import EventList
from timeline.accountlist import AccountList
from bibliography.bibliography import Bibliography
from utility.utils import flatten_list_of_lists, levenshtein
from datetime import datetime
from multiprocessing import Pool
from unicodedata import normalize
from argparse import ArgumentParser
from os.path import basename, exists, sep
from os import makedirs
from json import load, dumps
from urllib.parse import quote, unquote
from re import split
import logging

####################################################################
# This file serves as an entry point to analyse Wikipedia articles.#
####################################################################

def get_logger(directory):
    """Set up the logger."""
    logger = logging.getLogger("article_logger")
    formatter = logging.Formatter("%(asctime)s >>> %(message)s", "%F %H:%M:%S")
    logger.setLevel(logging.DEBUG)
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    stream_handler.setLevel(logging.INFO)
    file_handler = logging.FileHandler(directory + sep + "log.txt", "a")
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.DEBUG)
    logger.addHandler(stream_handler)
    logger.addHandler(file_handler)
    return logger

def occurrence(revision, result):
    return {"index":revision.index,"url":revision.url,"timestamp":revision.timestamp.string,"result":result}

def to_ascii(string):
    return normalize("NFD",string).encode("ASCII","ignore").decode("ASCII")

def to_lower(string):
    return string.lower()

def to_alnum(string):
    return "".join([character for character in string if character.isalnum() or character in [" "]])

def scroll_to_url(url, string):
    return url + "#:~:text=" + quote(string)

def exact_match(event_authors, source_text):
    return len([event_author for event_author in event_authors if event_author in source_text])/len(event_authors)

def jaccard(list1, list2):
    intersection = set(list1).intersection(set(list2))
    union = set(list1).union(set(list2))
    return len(intersection)/len(union)

def skat(gains, ideal, expected, provided):
    score = 0
    for position, item in enumerate(provided, 1):
        if item in gains:
            if expected.index(item) == provided.index(item):
                score += gains[item]/position
            else:
                score -= gains[item]/position
    return score/ideal

def analyse(event,
            revision,
            revision_text_lower,
            revision_text_lower_ascii,
            revision_text_lower_ascii_alnum,
            source_texts,
            source_texts_ascii,
            source_titles,
            source_titles_lower_ascii_alnum,
            referenced_author_sets_ascii,
            referenced_pmids,
            language,
            thresholds,
            article_title,
            first_or_index,
            heuristics):

    NED_LOW = thresholds["NORMALISED_EDIT_DISTANCE_THRESHOLDS"][0]
    NED_MID = thresholds["NORMALISED_EDIT_DISTANCE_THRESHOLDS"][1]
    NED_HIGH = thresholds["NORMALISED_EDIT_DISTANCE_THRESHOLDS"][2]
    EXACT = thresholds["RATIO_SCORE_THRESHOLD"]
    JACCARD = thresholds["JACCARD_SCORE_THRESHOLD"]
    SKAT = thresholds["SKAT_SCORE_THRESHOLD"]

    #VERBATIM EVENT TITLES
    if event.titles \
       and event.trace[article_title][first_or_index].get("verbatim", {}).get("titles", False) == None:
        verbatim_title_results = {}
        for event_bibkey, event_title in event.titles.items():
            if to_alnum(to_ascii(to_lower(event_title))) in revision_text_lower_ascii_alnum:
                verbatim_title_results[event_bibkey] = scroll_to_url(revision.url, event_title)
        if len(verbatim_title_results) == len(event.titles.values()):
            event.trace[article_title][first_or_index]["verbatim"]["titles"] = occurrence(revision, result=verbatim_title_results)
                
    ##############################################################################################

    #VERBATIM EVENT DOIS
    if event.dois \
       and event.trace[article_title][first_or_index].get("verbatim", {}).get("dois", False) == None:
        verbatim_doi_results = {}
        for event_bibkey, event_doi in event.dois.items():
            if event_doi and to_lower(event_doi) in revision_text_lower:
                verbatim_doi_results[event_bibkey] = scroll_to_url(revision.url, event_doi)
        if len(verbatim_doi_results) == len(event.dois):
            event.trace[article_title][first_or_index]["verbatim"]["dois"] = occurrence(revision, result=verbatim_doi_results)

    ##############################################################################################

    #VERBATIM EVENT PMIDS
    if event.pmids \
       and event.trace[article_title][first_or_index].get("verbatim", {}).get("pmids", False) == None:
        verbatim_pmid_results = {}
        for event_bibkey, event_pmid in event.pmids.items():
            if event_pmid and event_pmid in revision_text_lower:
                verbatim_pmid_results[event_bibkey] = scroll_to_url(revision.url, event_pmid)
        if len(verbatim_pmid_results) == len(event.pmids):
            event.trace[article_title][first_or_index]["verbatim"]["pmids"] = occurrence(revision, result=verbatim_pmid_results)

    #############################################################################################

    #RELAXED REFERENCE SEARCH
    if event.titles:
        if any([event.trace[article_title][first_or_index].get("relaxed", {}).get(key, False) == None for key in heuristics["relaxed"].keys()]):
            
            relaxed_results = {event_bibkey:{} for event_bibkey in event.titles}

            #TITLES
            for event_bibkey, event_title in event.titles.items():

                event_title_lower_ascii_alnum = to_alnum(to_ascii(to_lower(event_title)))

                for source_title_lower_ascii_alnum, source_text in zip(source_titles_lower_ascii_alnum, source_texts):

                    normalised_edit_distance = levenshtein(event_title_lower_ascii_alnum, source_title_lower_ascii_alnum)/len(event_title_lower_ascii_alnum)

                    if normalised_edit_distance < relaxed_results[event_bibkey].get("ned_low", (None, NED_LOW))[1]:
                        relaxed_results[event_bibkey]["ned_low"] = (source_text, normalised_edit_distance)
                    if normalised_edit_distance < relaxed_results[event_bibkey].get("ned_mid", (None, NED_MID))[1]:
                        relaxed_results[event_bibkey]["ned_mid"] = (source_text, normalised_edit_distance)
                    if normalised_edit_distance < relaxed_results[event_bibkey].get("ned_high", (None, NED_HIGH))[1]:
                        relaxed_results[event_bibkey]["ned_high"] = (source_text, normalised_edit_distance)

            if event.trace[article_title][first_or_index].get("relaxed", {}).get("ned <= " + str(NED_LOW), False) == None \
               and all([relaxed_results[event_bibkey].get("ned_low", False) for event_bibkey in event.titles]):
                relaxed_title_results_low = {event_bibkey:{"source_text":{"raw":relaxed_results[event_bibkey]["ned_low"][0],
                                                                          "goto":scroll_to_url(revision.url, relaxed_results[event_bibkey]["ned_low"][0])},
                                                           "normalised_edit_distance <= " + str(NED_LOW):relaxed_results[event_bibkey]["ned_low"][1]
                                                           } for event_bibkey in event.titles}
                event.trace[article_title][first_or_index]["relaxed"]["ned <= " + str(NED_LOW)] = occurrence(revision, result=relaxed_title_results_low)
                
            if event.trace[article_title][first_or_index].get("relaxed", {}).get("ned <= " + str(NED_MID), False) == None \
               and all([relaxed_results[event_bibkey].get("ned_mid", False) for event_bibkey in event.titles]):
                relaxed_title_results_mid = {event_bibkey:{"source_text":{"raw":relaxed_results[event_bibkey]["ned_mid"][0],
                                                                          "goto":scroll_to_url(revision.url, relaxed_results[event_bibkey]["ned_mid"][0])},
                                                           "normalised_edit_distance <= " + str(NED_MID):relaxed_results[event_bibkey]["ned_mid"][1]
                                                           } for event_bibkey in event.titles}
                event.trace[article_title][first_or_index]["relaxed"]["ned <= " + str(NED_MID)] = occurrence(revision, result=relaxed_title_results_mid)
                
            if event.trace[article_title][first_or_index].get("relaxed", {}).get("ned <= " + str(NED_HIGH), False) == None \
               and all([relaxed_results[event_bibkey].get("ned_high", False) for event_bibkey in event.titles]):
                relaxed_title_results_high = {event_bibkey:{"source_text":{"raw":relaxed_results[event_bibkey]["ned_high"][0],
                                                                           "goto":scroll_to_url(revision.url, relaxed_results[event_bibkey]["ned_high"][0])},
                                                            "normalised_edit_distance <= " + str(NED_HIGH):relaxed_results[event_bibkey]["ned_high"][1]
                                                            } for event_bibkey in event.titles}
                event.trace[article_title][first_or_index]["relaxed"]["ned <= " + str(NED_HIGH)] = occurrence(revision, result=relaxed_title_results_high)

            #AUTHORS
            if event.authors and event.trace[article_title][first_or_index].get("relaxed", {}).get("ned <= " + str(NED_HIGH), False):
                for event_bibkey, event_authors in event.authors.items():
                    
                    event_authors = [to_ascii(author) for author in event_authors]
                    gains = {author:len(event_authors) - event_authors.index(author) for author in event_authors}
                    ideal = sum([(gains.get(event_author, 0))/index for index,event_author in enumerate(event_authors, 1)])

                    for referenced_author_set_ascii, source_text, source_text_ascii in zip(referenced_author_sets_ascii, source_texts, source_texts_ascii):

                        exact_score = exact_match(event_authors, source_text_ascii)
                        jaccard_score = jaccard(event_authors, referenced_author_set_ascii)
                        skat_score = skat(gains, ideal, event_authors, referenced_author_set_ascii)

                        if exact_score >= relaxed_results[event_bibkey].get("exact", (None, EXACT))[1] and relaxed_results[event_bibkey].get("ned_high", (None, None))[0] == source_text:
                            relaxed_results[event_bibkey]["exact"] = (source_text, exact_score, relaxed_results[event_bibkey].get("ned_high")[1])
                        if jaccard_score >= relaxed_results[event_bibkey].get("jaccard", (None, JACCARD))[1] and relaxed_results[event_bibkey].get("ned_high", (None, None))[0] == source_text:
                            relaxed_results[event_bibkey]["jaccard"] = (source_text, jaccard_score, relaxed_results[event_bibkey].get("ned_high")[1])
                        if skat_score >= relaxed_results[event_bibkey].get("skat", (None, SKAT))[1] and relaxed_results[event_bibkey].get("ned_high", (None, None))[0] == source_text:
                            relaxed_results[event_bibkey]["skat"] = (source_text, skat_score, relaxed_results[event_bibkey].get("ned_high")[1])

                    if event.trace[article_title][first_or_index].get("relaxed", {}).get("ned_and_ratio", False) == None \
                       and all([relaxed_results[event_bibkey].get("exact", False) for event_bibkey in event.authors]):
                        events_in_references_by_authors_exact_match = {event_bibkey:{"source_text":{"raw":relaxed_results[event_bibkey]["exact"][0],
                                                                                                    "goto":scroll_to_url(revision.url, relaxed_results[event_bibkey]["exact"][0])},
                                                                                     "ratio_score": relaxed_results[event_bibkey]["exact"][1],
                                                                                     "normalised_edit_distance <= " + str(NED_HIGH):relaxed_results[event_bibkey]["exact"][2]
                                                                                     } for event_bibkey in event.authors}
                        event.trace[article_title][first_or_index]["relaxed"]["ned_and_ratio"] = occurrence(revision, result=events_in_references_by_authors_exact_match)

                    if event.trace[article_title][first_or_index].get("relaxed", {}).get("ned_and_jaccard", False) == None \
                       and all([relaxed_results[event_bibkey].get("jaccard", False) for event_bibkey in event.authors]):
                        events_in_references_by_authors_jaccard = {event_bibkey:{"source_text":{"raw":relaxed_results[event_bibkey]["jaccard"][0],
                                                                                                "goto":scroll_to_url(revision.url, relaxed_results[event_bibkey]["jaccard"][0])},
                                                                                 "jaccard_score": relaxed_results[event_bibkey]["jaccard"][1],
                                                                                 "normalised_edit_distance <= " + str(NED_HIGH):relaxed_results[event_bibkey]["jaccard"][2],
                                                                                 } for event_bibkey in event.authors}
                        event.trace[article_title][first_or_index]["relaxed"]["ned_and_jaccard"] = occurrence(revision, result=events_in_references_by_authors_jaccard)

                    if event.trace[article_title][first_or_index].get("relaxed", {}).get("ned_and_skat", False) == None \
                       and all([relaxed_results[event_bibkey].get("skat", False) for event_bibkey in event.authors]):
                        events_in_references_by_authors_skat = {event_bibkey:{"source_text":{"raw":relaxed_results[event_bibkey]["skat"][0],
                                                                                             "goto":scroll_to_url(revision.url, relaxed_results[event_bibkey]["skat"][0])},
                                                                              "skat_score": relaxed_results[event_bibkey]["skat"][1],
                                                                              "normalised_edit_distance <= " + str(NED_HIGH):relaxed_results[event_bibkey]["skat"][2]
                                                                              } for event_bibkey in event.authors}
                        event.trace[article_title][first_or_index]["relaxed"]["ned_and_skat"] = occurrence(revision, result=events_in_references_by_authors_skat)

    return event

if __name__ == "__main__":

    #Regex for matching DOIS (https://www.crossref.org/blog/dois-and-matching-regular-expressions)
    DOI_REGEXs = ["10\.\d{4,9}/[-\._;\(\)/:a-zA-Z0-9]+",
                 "doi:10\.\d{4,9}/[-\._;\(\)/:a-zA-Z0-9]+"]

    argument_parser = ArgumentParser()

    argument_parser.add_argument("-ad", "--articledir",
                                 help="The relative or absolute path to the directory where the articles reside.")
    argument_parser.add_argument("-ef", "--eventfile",
                                 help="The relative or absolute path to the event CSV.")
    argument_parser.add_argument("-od", "--outputdir",
                                 default="../analysis",
                                 help="The relative or absolute path to the directory the analysis will be saved.")
    argument_parser.add_argument("-a", "--articles",
                                 default="../data/relevant_articles/articles_arno.json",
                                 help="Either the relative of abolute path to a JSON file of articles " + \
                                      "or quoted string of comma-separated articles, " + \
                                      "e.g. 'Cas9,The CRISPR JOURNAL'.")
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
    argument_parser.add_argument("-m", "--mode",
                                 default="first_mentioned",
                                 help="'first_mentioned' to find first trace of events, 'full_trace' for all revisions")
    argument_parser.add_argument("-he", "--heuristics",
                                 default=("{'verbatim':{'titles':None,'dois':None,'pmids':None},"
                                           "'relaxed':{'ned <= ' + str(NED_LOW):None,'ned <= ' + str(NED_MID):None,'ned <= ' + str(NED_HIGH):None,"
                                                      "'ned_and_ratio':None,'ned_and_jaccard':None,'ned_and_skat':None}}"),
                                 help="Heuristics used to match event, e.g. '{'verbatim':{'titles':None,'dois':None,'pmids':None}}'")
    argument_parser.add_argument("-ned", "--normalised_edit_distance_thresholds",
                                 nargs="+",
                                 type=int,
                                 default=[0.2,0.3,0.4],
                                 help="Thresholds for normalised edit distance for titles in references; three values for low, medium and high.")
    argument_parser.add_argument("-ratio", "--ratio_score_threshold",
                                 type=int,
                                 default=1.0,
                                 help="Ratio score threshold for authors in reference.")
    argument_parser.add_argument("-jaccard", "--jaccard_score_threshold",
                                 type=int,
                                 default=0.8,
                                 help="Jaccard score threshold for authors in reference.")
    argument_parser.add_argument("-skat", "--skat_score_threshold",
                                 type=int,
                                 default=0.8,
                                 help="Skat score threshold for authors in reference.")

    args = vars(argument_parser.parse_args())

    article_directory = args["articledir"]
    event_file = args["eventfile"]
    output_directory = args["outputdir"] + sep + str(datetime.now())[:-7].replace(":","_").replace("-","_").replace(" ","_")
    conditions = args["conditions"]
    equalling = args["equalling"]
    language = args["language"]
    mode = args["mode"] if args["mode"] in ["first_mentioned", "full_trace"] else "first_mentioned"
    heuristics = args["heuristics"]
    thresholds = {"NORMALISED_EDIT_DISTANCE_THRESHOLDS":args["normalised_edit_distance_thresholds"],
                  "RATIO_SCORE_THRESHOLD":args["ratio_score_threshold"],
                  "JACCARD_SCORE_THRESHOLD":args["jaccard_score_threshold"],
                  "SKAT_SCORE_THRESHOLD":args["skat_score_threshold"]}

    if not exists(output_directory): makedirs(output_directory)

    logger = get_logger(output_directory)
    
    if exists(args["articles"]):
        article_titles = flatten_list_of_lists(load(open(args["articles"])).values())
    else:
        article_titles = [article.strip() for article in split(" *, *", args["articles"])]

    bibliography = Bibliography("../data/tracing-innovations-lit.bib")
    accountlist = AccountList("../data/CRISPR_accounts.csv")

    logger.info("Analysing articles [" + ", ".join(article_titles) + "]")
    logger.info("Using event file: " + basename(event_file))
    logger.info("Using events with conditions: " + ", ".join(conditions if conditions else ["-"]))
    logger.info("Equalling events to attributes: " + ", ".join(equalling if equalling else ["-"]))
    logger.info("Trace mode: " + mode)
    logger.info("Using the below thresholds:")
    for threshold in thresholds:
        logger.info(threshold + ": " + str(thresholds[threshold]))    
    
    for article_title in article_titles:

        eventlist = EventList(event_file, bibliography, accountlist, conditions, equalling)

        logger.info(article_title)

        filename = quote(article_title.replace(" ","_"), safe="")
        filepath = article_directory + sep + filename + "_" + language
        if not exists(filepath):
            logger.info(filepath + " does not exist.")
            continue
        
        article = Article(filepath)
        revisions = article.yield_revisions()
        revision = next(revisions, None)

        print("Number of events:", len(eventlist.events))

        NED_LOW = thresholds["NORMALISED_EDIT_DISTANCE_THRESHOLDS"][0]
        NED_MID = thresholds["NORMALISED_EDIT_DISTANCE_THRESHOLDS"][1]
        NED_HIGH = thresholds["NORMALISED_EDIT_DISTANCE_THRESHOLDS"][2]

        if mode == "first_mentioned":
            for event in eventlist.events:
                event.trace[article_title] = {"first_mentioned":eval(heuristics)}
        else:
            for event in eventlist.events:
                event.trace[article_title] = {}

        while revision:

            print(revision.index)

            if mode == "full_trace":
                for event in eventlist.events:
                    event.trace[article_title][revision.index] = eval(heuristics)

            #FIX REVISION URL BY REPLACING SPACES WITH UNDERSCORES
            revision.url = revision.url.replace(" ", "_")

            ### The lowered full text.
            revision_text_lower = to_lower(revision.get_text())
            ### The lowered ASCII-normalised full text.
            revision_text_lower_ascii = to_ascii(to_lower(revision_text_lower))
            ### The lowered ASCII-normalised full text, stripped of any characters except latin alphabet and spaces.
            revision_text_lower_ascii_alnum = to_alnum(revision_text_lower_ascii)
            ### The sources of the revision, i.e. 'References' and 'Further Reading' elements.
            sources = revision.get_references() + revision.get_further_reading()
            ### The texts of all sources, both raw and ASCII-normalised.
            source_texts = [source.get_text().strip() for source in sources]
            source_texts_ascii = [to_ascii(source_text) for source_text in source_texts]
            ### All titles occuring in 'References' and 'Further Reading', both raw and ASCII-normalised and lowered and stripped of any characters except latin alphabet and spaces.
            source_titles = [source.get_title(language) for source in sources]
            source_titles_lower_ascii_alnum = [to_alnum(to_ascii(to_lower(source_title))) for source_title in source_titles]
            ### All authors occuring in 'References' and 'Further Reading', ASCII-normalised.
            referenced_author_sets_ascii = [[to_ascii(author[0]) for author in source.get_authors(language)] for source in sources]
            ### All PMIDs occuring in 'References' and 'Further Reading'.
            referenced_pmids = set([])#set(flatten_list_of_lists([source.get_pmids() for source in sources]))

            with Pool(24) as pool:
                eventlist.events = pool.starmap(analyse,
                                                [(event,
                                                  revision,
                                                  revision_text_lower,
                                                  revision_text_lower_ascii,
                                                  revision_text_lower_ascii_alnum,
                                                  source_texts,
                                                  source_texts_ascii,
                                                  source_titles,
                                                  source_titles_lower_ascii_alnum,
                                                  referenced_author_sets_ascii,
                                                  referenced_pmids,
                                                  language,
                                                  thresholds,
                                                  article_title,
                                                  mode if mode == "first_mentioned" else revision.index,
                                                  eval(heuristics))
                                                 for event in eventlist.events])

            revision = next(revisions, None)

        logger.info("Done.")

        eventlist.write_text(output_directory + sep + filename + "." + "txt")
        eventlist.write_json(output_directory + sep + filename + "." + "json")
