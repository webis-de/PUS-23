from scraper.scraper import Scraper
from utility.logger import Logger
from json import load

def flatten_list_of_lists(list_of_lists):
    return [item for sublist in list_of_lists for item in sublist]

with open("../data/wikipedia_articles.json") as file:
    wikipedia_articles = flatten_list_of_lists(load(file).values())

print(wikipedia_articles)

with Logger("../extractions (copy 1)") as logger:
    for article in wikipedia_articles:
        with Scraper(logger, article, "en") as scraper:
            scraper.scrape("../extractions (copy 1)")
