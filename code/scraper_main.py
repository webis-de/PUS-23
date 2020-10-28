from scraper.scraper import Scraper
from utility.logger import Logger
from utility.utils import flatten_list_of_lists
from json import load
from re import split
from argparse import ArgumentParser
from datetime import datetime

################################################################
# This file serves as an entry point to test the Scraper class.#
################################################################


if __name__ == "__main__":

    date = datetime.now()
    date = "-".join([str(item) for item in [date.year, date.month, date.day - 1]])

    argument_parser = ArgumentParser()

    argument_parser.add_argument("-dir", "--directory",
                                 default="../articles",
                                 help="The relative or absolute path to directory to which the revisions will be saved.")
    argument_parser.add_argument("-a", "--articles",
                                 default="../data/articles_custom.json",
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
    args = vars(argument_parser.parse_args())

    """
    Load articles and flatten to one list if from file or split if connected with ','.
    """
    ARTICLES = args["articles"]
    try:
        with open(ARTICLES) as file:
            wikipedia_articles = flatten_list_of_lists(load(file).values())
    except FileNotFoundError:
        wikipedia_articles = [article.strip() for article in split(" *, *", ARTICLES)]
    """
    Select an output directory.
    """
    DIRECTORY = args["directory"]

    """
    Select the language, either 'en' or 'de'.
    """
    LANGUAGE = args["language"]

    """
    Select a deadline with format YYYY-MM-DD. Only revision before that date will be scraped.
    """
    DEADLINE = args["deadline"]

    """
    Select the first n revisions you want to scrape (float("inf") will scrape all)
    FOR TESTING PURPOSES
    """
    NUMBER = args["number"]

    """
    Select articles you want to scrape. For test purposes, use the second list,
    which contains small articles of a few kilobyte each (including HTML).
    """
    ARTICLES = wikipedia_articles
    with Logger(DIRECTORY) as logger:
        for article in ARTICLES:
            with Scraper(logger, article, LANGUAGE) as scraper:
                scraper.scrape(directory = DIRECTORY,
                               deadline = DEADLINE,
                               number = NUMBER)
