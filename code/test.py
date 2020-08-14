from scraper.scraper import Scraper
from entity.article import Article
from entity.bibliography import Bibliography
from utility.logger import Logger
from os import popen, remove, rename, rmdir
from os.path import sep
from json import load
from hashlib import sha256

TITLE = "CRISPR"
LANGUAGE = "de"
FILENAME = TITLE + "_" + LANGUAGE

def checksum(filepath):
    sha256_hash = sha256()
    with open(filepath,"rb") as f:
        for byte_block in iter(lambda: f.read(4096),b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def test_full_and_updated_scrape(logger):    
    DIRECTORY = ".." + sep + "test" + sep + "test_full_and_updated_scrape"
    FILEPATH = DIRECTORY + sep + FILENAME

    logger.start("Testing singlescraping full and update")

    #scrape article in full
    logger.start_check("Singlescraping (full)...")
    with Scraper(logger = logger, title = TITLE, language = LANGUAGE) as scraper:
        scraper.scrape(DIRECTORY, html=False)
        number_of_full_scraped_revisions = scraper.revision_count
    full_scrape_checksum = checksum(FILEPATH)
    remove(FILEPATH)
    logger.end_check("Done.")

    #scrape first five revisions
    logger.start_check("Singlescraping (update)...")
    with Scraper(logger = logger, title = TITLE, language = LANGUAGE) as scraper:
        scraper.scrape(DIRECTORY, html=False, number=5)
    #scrape remaining revisions
    with Scraper(logger = logger, title = TITLE, language = LANGUAGE) as scraper:
        scraper.scrape(DIRECTORY, html=False)
        number_of_updated_scraped_revisions = scraper.revision_count
    update_scrape_checksum = checksum(FILEPATH)
    rename(FILEPATH, FILEPATH + "_renamed")
    logger.end_check("Done.")

    #assert full and updated scrape match
    assert full_scrape_checksum == update_scrape_checksum
    assert number_of_full_scraped_revisions == number_of_updated_scraped_revisions

    logger.stop("Singlescraping test successful.", 1)
    
def test_multi_scrape_with_5_revisions(logger):
    DIRECTORY = ".." + sep + "test" + sep + "test_multi_scrape"

    ARTICLES = {"CRISPR":"ad28f439c90e4ef8767be2d5547920333207ccd17d75a48e1576eedce637d7d1",
                "CRISPR gene editing":"8cca970732d5361181bfff3b7d1dbb2d925b63e30c95764e9613621b021bb948",
                "Cas9":"058fe4d9d53bce018908aafc94fb5747b4c8a36c2f57a73afb9bd18663a969b7",
                "Trans-activating crRNA":"3604eb62fd31d03b491496bea65b41c577f5a18c6dca1b11f8ebfd45c62523c9",
                "CRISPR/Cpf1":"fc6856822f8681f9fb02fd45eaf3fdf7963a2e40f58da9b17ac9f5f1e3028767"}
    
    #scrape first five revisions of each article and assert checksum code state 14 August 2020
    logger.start("Testing multiscraping " + ", ".join(ARTICLES) + "...")
    for article in ARTICLES:
        with Scraper(logger = LOGGER, title = article, language = "en") as scraper:
            scraper.scrape(DIRECTORY, html=False, number=5)
            assert checksum(DIRECTORY + sep + article.replace("/","-") + "_" + "en") == ARTICLES[article]
    logger.stop("Multiscraping test successful.", 1)

def test_pipeline(logger):
    DIRECTORY = ".." + sep + "test" + sep + "test_pipeline"
    FILEPATH = DIRECTORY + sep + FILENAME

    logger.start("Testing pipeline...")
    
    #scrape article
    with Scraper(logger = logger, title = TITLE, language = LANGUAGE) as scraper:
        scraper.scrape(DIRECTORY, html=False)

    #load article from file
    article = Article(FILEPATH)
    article.plot_revision_distribution_to_file(DIRECTORY)

    #load bibliography from file
    bibliography = Bibliography(".." + sep + "data" + sep + "bibliography_marion.bib")
    bibliography.plot_publication_distribution_to_file(DIRECTORY)

    #track bibkeys and print/plot
    tracks = article.track_bibkeys_in_article(["titles", "dois", "authors"], bibliography)
    for track in tracks.items():
        article.write_track_to_file(track, DIRECTORY)
        article.plot_track_to_file(track, DIRECTORY)

    #assert revision information
    assert article.revisions[0].revid == 69137443
    assert article.revisions[0].timestamp.string == "2010-01-11 02:11:54"
    assert article.revisions[0].user == "Tinz"
    assert article.revisions[0].userid == 92881
    assert article.revisions[0].comment == "neu, wird noch erweitert"

    logger.stop("Pipeline test successfull.", 1)

with Logger(".." + sep + "test" + sep + "logs") as LOGGER:
    test_full_and_updated_scrape(LOGGER)
    test_multi_scrape_with_5_revisions(LOGGER)
    test_pipeline(LOGGER)
