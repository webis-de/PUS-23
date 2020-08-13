from scraper import Scraper
from article import Article
from bibliography.bibliography import Bibliography
from utility.logger import Logger
from os import popen, remove, rename, rmdir
from os.path import sep
from json import load

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
    
    assert full_scrape_checksum == update_scrape_checksum
    assert number_of_full_scraped_revisions == number_of_updated_scraped_revisions
    
def test_multi_scrape_with_5_revisions(logger):
    DIRECTORY = ".." + sep + "test" + sep + "test_multi_scrape"
    #load Arno's list of relevant Wikipedia articles
    with open("../data/wikipedia_articles.json") as articles_file:
        wikipedia_articles = load(articles_file)

    #flatten dictionary
    ARTICLES = [article for values in wikipedia_articles.values() for article in values]

    #scrape first five revisions of each article
    logger.start("Scraping " + ", ".join(ARTICLES))
    for article in ARTICLES:
        with Scraper(logger = LOGGER, title = article, language = "en") as scraper:
            scraper.scrape(DIRECTORY, html=False, number=5)

def test_pipeline(logger):
    DIRECTORY = ".." + sep + "test" + sep + "test_pipeline"
    TITLE = "CRISPR"
    LANGUAGE = "de"
    FILENAME = TITLE + "_" + LANGUAGE
    FILEPATH = DIRECTORY + sep + FILENAME

    #scrape article
    with Scraper(logger = logger, title = TITLE, language = LANGUAGE) as scraper:
        scraper.scrape(DIRECTORY, html=False)

    #access revision information
    article = Article(FILEPATH)
    print(article.revisions[0].revid)
    print(article.revisions[0].timestamp.string)
    print(article.revisions[0].user)
    print(article.revisions[0].userid)
    print(article.revisions[0].comment)

    #load bibliography
    bibliography = Bibliography(".." + sep + "data" + sep + "Referenzen_crispr_cas.csv")

    #track bibkeys and print/plot
    tracks = article.track_bibkeys_in_article(["titles", "dois", "authors"], bibliography)
    for track in tracks.items():
        article.write_track_to_file(track, DIRECTORY)
        article.plot_track_to_file(track, DIRECTORY)

LOGGER = Logger(".." + sep + "test" + sep + "logs")
test_full_and_updated_scrape(LOGGER)
test_multi_scrape_with_5_revisions(LOGGER)
test_pipeline(LOGGER)
LOGGER.close()
