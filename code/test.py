from utility.logger import Logger
from scraper import Scraper
from json import load
from os import popen, remove, rename, rmdir
from os.path import sep

def test_full_and_updated_scrape(logger):    
    DIRECTORY = ".." + sep + "test" + sep + "test_single_scrape"
    TITLE = "CRISPR"
    LANGUAGE = "de"
    filename = TITLE + "_" + LANGUAGE
    filepath = DIRECTORY + sep + filename
    
    #scrape article in full
    with Scraper(logger = logger, title = TITLE, language = LANGUAGE) as scraper:
        scraper.scrape(DIRECTORY, html=False)
        number_of_full_scraped_revisions = scraper.revision_count
    full_scrape_checksum = popen("sha256sum " + filepath).read().split(" ")[0]
    remove(filepath)
    
    #scrape first five revisions
    with Scraper(logger = logger, title = TITLE, language = LANGUAGE) as scraper:
        scraper.scrape(DIRECTORY, html=False, number=5)
    #scrape remaining revisions
    with Scraper(logger = logger, title = TITLE, language = LANGUAGE) as scraper:
        scraper.scrape(DIRECTORY, html=False)
        number_of_updated_scraped_revisions = scraper.revision_count
    update_scrape_checksum = popen("sha256sum " + filepath).read().split(" ")[0]
    remove(filepath)
    rmdir(DIRECTORY)
    
    assert full_scrape_checksum == update_scrape_checksum
    assert number_of_full_scraped_revisions == number_of_updated_scraped_revisions
    
def test_multi_scrape_with_5_revisions(logger):    
    with open("../data/wikipedia_articles.json") as articles_file:
        wikipedia_articles = load(articles_file)

    articles = [article for values in wikipedia_articles.values() for article in values]

    logger.start("Scraping " + ", ".join(articles))
    for article in articles:
        with Scraper(logger = LOGGER, title = article, language = "en") as scraper:
            scraper.scrape(".." + sep + "test" + sep + "test_multi_scrape", html=False, number=5)

LOGGER = Logger(".." + sep + "test" + sep + "logs")
test_full_and_updated_scrape(LOGGER)
test_multi_scrape_with_5_revisions(LOGGER)
LOGGER.close()
