from scraper.scraper import Scraper
from utility.logger import Logger
from utility.utils import flatten_list_of_lists
from json import load


################################################################
# This file serves as an entry point to test the Scraper class.#
################################################################


if __name__ == "__main__":

    """
    Load all Wikipedia articles collected by Arno and flatten to one list
    """
    with open("../data/wikipedia_articles.json") as file:
        wikipedia_articles = flatten_list_of_lists(load(file).values())

    """
    Select an output directory.
    """
    DIRECTORY = "../extractions"

    """
    Select the first n revisions you want to scrape (float("inf") will scrape all)
    FOR TESTING PURPOSES
    """
    NUMBER = float("inf")

    """
    Select the language, either 'en' or 'de'.
    """
    LANGUAGE = "en"

    """
    Select articles you want to scrape. For test purposes, use the second list,
    which contains small articles of a few kilobyte each (including HTML).
    """
    #ARTICLES = wikipedia_articles
    ARTICLES = ["CRISPR"]
    with Logger(DIRECTORY) as logger:
        for article in ARTICLES:
            with Scraper(logger, article, LANGUAGE) as scraper:
                scraper.scrape(directory = DIRECTORY,
                               number = NUMBER)
