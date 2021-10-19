from scraper.scraper import Scraper
from utility.utils import flatten_list_of_lists
from json import load
from re import split
from argparse import ArgumentParser
from datetime import datetime

#########################################################
# This file serves as an entry point to scrape articles.#
#########################################################

if __name__ == "__main__":

    date = datetime.now()
    date = "-".join([str(item) for item in [date.year, date.month, date.day - 1]])

    argument_parser = ArgumentParser()

    argument_parser.add_argument("-dir", "--directory",
                                 default="../articles",
                                 help="The relative or absolute path to the directory " + \
                                      "to which the revisions will be saved.")
    argument_parser.add_argument("-a", "--articles",
                                 default="../data/relevant_articles/CRISPR_articles.json",
                                 help="Either the relative of abolute path to a JSON file of articles " + \
                                      "or quoted string of comma-separated articles, " + \
                                      "e.g. 'Cas9,The CRISPR JOURNAL'.")
    argument_parser.add_argument("-l", "--language",
                                 default="en",
                                 help="en or de, defaults to en.")
    argument_parser.add_argument("-dl", "--deadline",
                                 default=date,
                                 help="Only revisions BEFORE the given date will be scraped. " +\
                                      "Use format YYYY-MM-DD. Defaults to yesterday.")
    argument_parser.add_argument("-n", "--number",
                                 default=float("inf"),
                                 type=float,
                                 help="The maximum number of revisions to scrape, defaults to infinity.")
    argument_parser.add_argument("--nohtml",
                                 action='store_false',
                                 help="Omit the HTML of the revisions.")
    argument_parser.add_argument("--noredirect",
                                 action='store_false',
                                 help="Do not get redirect of article.")
    args = vars(argument_parser.parse_args())

    #Load articles and flatten to one list if from file or split if connected with ','.
    ARTICLES = args["articles"]
    try:
        with open(ARTICLES) as file:
            if ".json" in ARTICLES:
                wikipedia_articles = flatten_list_of_lists(load(file).values())
            if ".txt" in ARTICLES:
                wikipedia_articles = [line.strip() for line in file.readlines()]
    except FileNotFoundError:
        wikipedia_articles = [article.strip() for article in split(" *, *", ARTICLES)]

    DIRECTORY = args["directory"]
    LANGUAGE = args["language"]
    DEADLINE = args["deadline"]
    NUMBER = args["number"]
    GETHTML = args["nohtml"]
    GETREDIRECT = args["noredirect"]

    ARTICLES = wikipedia_articles
    for article in ARTICLES:
        with Scraper(DIRECTORY, article, LANGUAGE, GETREDIRECT) as scraper:
            scraper.scrape(directory = DIRECTORY,
                           deadline = DEADLINE,
                           number = NUMBER,
                           verbose = True,
                           gethtml = GETHTML)
