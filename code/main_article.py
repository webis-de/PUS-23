from article.article import Article
from timeline.eventlist import EventList
from timeline.accountlist import AccountList
from bibliography.bibliography import Bibliography
from utility.utils import flatten_list_of_lists, levenshtein
from utility.logger import Logger
from multiprocessing import Pool
from unicodedata import normalize
from argparse import ArgumentParser
from os.path import basename, exists, sep
from os import makedirs
from json import load, dumps
from urllib.parse import quote, unquote

####################################################################
# This file serves as an entry point to analyse Wikipedia articles.#
####################################################################

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

def analyse(event, revision, revision_text_lower, revision_text_lower_ascii, revision_text_lower_ascii_alnum, source_texts, source_texts_ascii, source_titles, source_titles_lower_ascii_alnum, referenced_author_sets_ascii, referenced_pmids, language, thresholds):

    NED_LOW = thresholds["NORMALISED_EDIT_DISTANCE_THRESHOLDS"][0]
    NED_MID = thresholds["NORMALISED_EDIT_DISTANCE_THRESHOLDS"][1]
    NED_HIGH = thresholds["NORMALISED_EDIT_DISTANCE_THRESHOLDS"][2]
    EXACT = thresholds["RATIO_SCORE_THRESHOLD"]
    JACCARD = thresholds["JACCARD_SCORE_THRESHOLD"]
    SKAT = thresholds["SKAT_SCORE_THRESHOLD"]

    #VERBATIM EVENT TITLES
    if event.titles and not event.first_mentioned["verbatim"].get("titles", None):
            verbatim_title_results = {}
            for event_bibkey, event_title in event.titles.items():
                if to_alnum(to_ascii(to_lower(event_title))) in revision_text_lower_ascii_alnum:
                    verbatim_title_results[event_bibkey] = scroll_to_url(revision.url, event_title)
            if len(verbatim_title_results) == len(event.titles.values()):
                event.first_mentioned["verbatim"]["titles"] = occurrence(revision, result=verbatim_title_results)
                
    ##############################################################################################

    #VERBATIM EVENT DOIS
    if event.dois and not event.first_mentioned["verbatim"].get("dois", None):
        verbatim_doi_results = {event_doi:scroll_to_url(revision.url, event_doi) for event_doi in event.dois if event_doi and to_lower(event_doi) in revision_text_lower}
        if len(verbatim_doi_results) == len(event.dois):
            event.first_mentioned["verbatim"]["dois"] = occurrence(revision, result=verbatim_doi_results)

    ##############################################################################################

    #VERBATIM EVENT PMIDS
    if event.pmids and not event.first_mentioned["verbatim"].get("pmids", None):
        verbatim_pmid_results = {event_pmid:scroll_to_url(revision.url, event_pmid) for event_pmid in event.pmids if event_pmid in referenced_pmids}
        if len(verbatim_pmid_results) == len(event.pmids):
            event.first_mentioned["verbatim"]["pmids"] = occurrence(revision, result=verbatim_pmid_results)

    #############################################################################################

    #RELAXED REFERENCE SEARCH
    if event.titles:
        if not event.first_mentioned["relaxed"].get("ned <= " + str(NED_LOW), None) or \
           not event.first_mentioned["relaxed"].get("ned <= " + str(NED_MID), None) or \
           not event.first_mentioned["relaxed"].get("ned <= " + str(NED_HIGH), None) or \
           not event.first_mentioned["relaxed"].get("ned_and_ratio", None) or \
           not event.first_mentioned["relaxed"].get("ned_and_jaccard", None) or \
           not event.first_mentioned["relaxed"].get("ned_and_skat", None):
            
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

            if not event.first_mentioned["relaxed"].get("ned <= " + str(NED_LOW), None) and all([relaxed_results[event_bibkey].get("ned_low", False) for event_bibkey in event.titles]):
                relaxed_title_results_low = {event_bibkey:{"source_text":{"raw":relaxed_results[event_bibkey]["ned_low"][0],
                                                                          "goto":scroll_to_url(revision.url, relaxed_results[event_bibkey]["ned_low"][0])},
                                                           "normalised_edit_distance <= " + str(NED_LOW):relaxed_results[event_bibkey]["ned_low"][1]
                                                           } for event_bibkey in event.titles}
                event.first_mentioned["relaxed"]["ned <= " + str(NED_LOW)] = occurrence(revision, result=relaxed_title_results_low)
                
            if not event.first_mentioned["relaxed"].get("ned <= " + str(NED_MID), None) and all([relaxed_results[event_bibkey].get("ned_mid", False) for event_bibkey in event.titles]):
                relaxed_title_results_mid = {event_bibkey:{"source_text":{"raw":relaxed_results[event_bibkey]["ned_mid"][0],
                                                                          "goto":scroll_to_url(revision.url, relaxed_results[event_bibkey]["ned_mid"][0])},
                                                           "normalised_edit_distance <= " + str(NED_MID):relaxed_results[event_bibkey]["ned_mid"][1]
                                                           } for event_bibkey in event.titles}
                event.first_mentioned["relaxed"]["ned <= " + str(NED_MID)] = occurrence(revision, result=relaxed_title_results_mid)
                
            if not event.first_mentioned["relaxed"].get("ned <= " + str(NED_HIGH), None) and all([relaxed_results[event_bibkey].get("ned_high", False) for event_bibkey in event.titles]):
                relaxed_title_results_high = {event_bibkey:{"source_text":{"raw":relaxed_results[event_bibkey]["ned_high"][0],
                                                                           "goto":scroll_to_url(revision.url, relaxed_results[event_bibkey]["ned_high"][0])},
                                                            "normalised_edit_distance <= " + str(NED_HIGH):relaxed_results[event_bibkey]["ned_high"][1]
                                                            } for event_bibkey in event.titles}
                event.first_mentioned["relaxed"]["ned <= " + str(NED_HIGH)] = occurrence(revision, result=relaxed_title_results_high)

            #AUTHORS
            if event.authors:
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

                    if not event.first_mentioned["relaxed"].get("ned_and_ratio", None) and all([relaxed_results[event_bibkey].get("exact", False) for event_bibkey in event.authors]):
                        events_in_references_by_authors_exact_match = {event_bibkey:{"source_text":{"raw":relaxed_results[event_bibkey]["exact"][0],
                                                                                                    "goto":scroll_to_url(revision.url, relaxed_results[event_bibkey]["exact"][0])},
                                                                                     "ratio_score": relaxed_results[event_bibkey]["exact"][1],
                                                                                     "normalised_edit_distance <= " + str(NED_HIGH):relaxed_results[event_bibkey]["exact"][2]
                                                                                     } for event_bibkey in event.authors}
                        event.first_mentioned["relaxed"]["ned_and_ratio"] = occurrence(revision, result=events_in_references_by_authors_exact_match)

                    if not event.first_mentioned["relaxed"].get("ned_and_jaccard", None) and all([relaxed_results[event_bibkey].get("jaccard", False) for event_bibkey in event.authors]):
                        events_in_references_by_authors_jaccard = {event_bibkey:{"source_text":{"raw":relaxed_results[event_bibkey]["jaccard"][0],
                                                                                                "goto":scroll_to_url(revision.url, relaxed_results[event_bibkey]["jaccard"][0])},
                                                                                 "jaccard_score": relaxed_results[event_bibkey]["jaccard"][1],
                                                                                 "normalised_edit_distance <= " + str(NED_HIGH):relaxed_results[event_bibkey]["jaccard"][2],
                                                                                 } for event_bibkey in event.authors}
                        event.first_mentioned["relaxed"]["ned_and_jaccard"] = occurrence(revision, result=events_in_references_by_authors_jaccard)

                    if not event.first_mentioned["relaxed"].get("ned_and_skat", None) and all([relaxed_results[event_bibkey].get("skat", False) for event_bibkey in event.authors]):
                        events_in_references_by_authors_skat = {event_bibkey:{"source_text":{"raw":relaxed_results[event_bibkey]["skat"][0],
                                                                                             "goto":scroll_to_url(revision.url, relaxed_results[event_bibkey]["skat"][0])},
                                                                              "skat_score": relaxed_results[event_bibkey]["skat"][1],
                                                                              "normalised_edit_distance <= " + str(NED_HIGH):relaxed_results[event_bibkey]["skat"][2]
                                                                              } for event_bibkey in event.authors}
                        event.first_mentioned["relaxed"]["ned_and_skat"] = occurrence(revision, result=events_in_references_by_authors_skat)

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
    output_directory = args["outputdir"]
    articles = args["articlelist"]
    conditions = args["conditions"]
    equalling = args["equalling"]
    language = args["language"]
    thresholds = {"NORMALISED_EDIT_DISTANCE_THRESHOLDS":args["normalised_edit_distance_thresholds"],
                  "RATIO_SCORE_THRESHOLD":args["ratio_score_threshold"],
                  "JACCARD_SCORE_THRESHOLD":args["jaccard_score_threshold"],
                  "SKAT_SCORE_THRESHOLD":args["skat_score_threshold"]}

    logger = Logger(output_directory)
    output_directory = logger.directory

    if not exists(output_directory): makedirs(output_directory)
    
    if not articles: articles = flatten_list_of_lists(load(open(args["articlefile"])).values())

    bibliography = Bibliography("../data/tracing-innovations-lit.bib")
    accountlist = AccountList("../data/CRISPR_accounts.csv")

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

        print(len(eventlist.events))

        NED_LOW = thresholds["NORMALISED_EDIT_DISTANCE_THRESHOLDS"][0]
        NED_MID = thresholds["NORMALISED_EDIT_DISTANCE_THRESHOLDS"][1]
        NED_HIGH = thresholds["NORMALISED_EDIT_DISTANCE_THRESHOLDS"][2]

        for event in eventlist.events:
            event.first_mentioned = {
                "verbatim":{
                    "titles":None,
                    "dois":None,
                    "pmids":None},
                "relaxed":{
                    "ned <= " + str(NED_LOW):None,
                    "ned <= " + str(NED_MID):None,
                    "ned <= " + str(NED_HIGH):None,
                    "ned_and_ratio":None,
                    "ned_and_jaccard":None,
                    "ned_and_skat":None}
                        }

        while revision:

            print(revision.index)

            #FIX REVISION URL BY REPLACEING SPACES WITH UNDERSCORES
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
            referenced_pmids = set(flatten_list_of_lists([source.get_pmids() for source in sources]))

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
                                                  thresholds)
                                                 for event in eventlist.events])

            revision = next(revisions, None)

        logger.end_check("Done.")

        eventlist.write_text(output_directory + sep + filename + "_" + language + "." + "txt")
        eventlist.write_json(output_directory + sep + filename + "_" + language + "." + "json")

    logger.close()
