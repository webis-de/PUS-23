from scraper.scraper import Scraper
from utility.logger import Logger
from json import load


##########################################################
# This file serves as an entry point to test the Scraper.#
##########################################################


def flatten_list_of_lists(list_of_lists):
    """
    Flattens list of lists to one list, i.e.
    [[e1,e2,e3],[e4,e5,e6],...] => [e1,e2,e3,e4,e5,e6,...]

    Args:
        list_of_lists: A list of lists.

    Returns:
        A flattened list of elements of each list in the list of lists.
    """
    return [item for sublist in list_of_lists for item in sublist]

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
    Set HTML if you want to scrape HTML as well
    FOR TESTING ONLY: Updating a revision scrape will only scrape scrape HTML for new revisions.
    """
    HTML = True

    """
    Select the first n revisions you want to scrape (float("inf") will scrape all)
    FOR TESTING PURPOSES
    """
    NUMBER = float("inf")

    """
    Select articles you want to scrape. For test purposes, use the second list,
    which contains small articles of a few kilobyte each (including HTML).
    """
    #ARTICLES = wikipedia_articles
    ARTICLES = ["CRISPR"]
    with Logger(DIRECTORY) as logger:
        for article in ARTICLES:
            with Scraper(logger, article, "de") as scraper:
                scraper.scrape(directory = DIRECTORY,
                               html = HTML,
                               number = NUMBER)
