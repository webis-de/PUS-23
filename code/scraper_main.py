from scraper.scraper import Scraper
from utility.logger import Logger
from utility.utils import flatten_list_of_lists
from json import load
from argparse import ArgumentParser

################################################################
# This file serves as an entry point to test the Scraper class.#
################################################################


if __name__ == "__main__":

    argument_parser = ArgumentParser()

    argument_parser.add_argument("-dir", "--directory", default="../articles")
    argument_parser.add_argument("-art", "--articles", default="../data/wikipedia_articles.json")
    argument_parser.add_argument("-lang", "--language", default="en")
    args = vars(argument_parser.parse_args())

    """
    Load articles and flatten to one list
    """
    with open(args["articles"]) as file:
        wikipedia_articles = flatten_list_of_lists(load(file).values())

    """
    Select an output directory.
    """
    DIRECTORY = args["directory"]

    """
    Select the language, either 'en' or 'de'.
    """
    LANGUAGE = args["language"]

    """
    Select the first n revisions you want to scrape (float("inf") will scrape all)
    FOR TESTING PURPOSES
    """
    NUMBER = float("inf")

    """
    Select articles you want to scrape. For test purposes, use the second list,
    which contains small articles of a few kilobyte each (including HTML).
    """
    ARTICLES = wikipedia_articles
    with Logger(DIRECTORY) as logger:
        for article in ARTICLES:
            with Scraper(logger, article, LANGUAGE) as scraper:
                scraper.scrape(directory = DIRECTORY,
                               number = NUMBER)
