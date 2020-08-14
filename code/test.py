from scraper import Scraper
from article import Article
from bibliography.bibliography import Bibliography
from bibliography.bibliography import Bibentry
from utility.logger import Logger
from os import popen, remove, rename, rmdir
from os.path import sep
from json import load

TITLE = "CRISPR"
LANGUAGE = "de"
FILENAME = TITLE + "_" + LANGUAGE

def test_full_and_updated_scrape(logger):    
    DIRECTORY = ".." + sep + "test" + sep + "test_full_and_updated_scrape"
    FILEPATH = DIRECTORY + sep + FILENAME

    logger.start("Testing singlescraping full and update")

    logger.start_check("Singlescraping (full)...")
    #scrape article in full
    with Scraper(logger = logger, title = TITLE, language = LANGUAGE) as scraper:
        scraper.scrape(DIRECTORY, html=False)
        number_of_full_scraped_revisions = scraper.revision_count
    full_scrape_checksum = popen("sha256sum " + FILEPATH).read().split(" ")[0]
    remove(FILEPATH)
    logger.end_check("Done.")

    logger.start_check("Singlescraping (update)...")
    #scrape first five revisions
    with Scraper(logger = logger, title = TITLE, language = LANGUAGE) as scraper:
        scraper.scrape(DIRECTORY, html=False, number=5)
    #scrape remaining revisions
    with Scraper(logger = logger, title = TITLE, language = LANGUAGE) as scraper:
        scraper.scrape(DIRECTORY, html=False)
        number_of_updated_scraped_revisions = scraper.revision_count
    update_scrape_checksum = popen("sha256sum " + FILEPATH).read().split(" ")[0]
    remove(FILEPATH)
    logger.end_check("Done.")

    #assert full and update scrape match
    assert full_scrape_checksum == update_scrape_checksum
    assert number_of_full_scraped_revisions == number_of_updated_scraped_revisions

    logger.stop("Singlescraping test successful.", 1)
    
def test_multi_scrape_with_5_revisions(logger):
    DIRECTORY = ".." + sep + "test" + sep + "test_multi_scrape"
    #load Arno's list of relevant Wikipedia articles
    with open("../data/wikipedia_articles.json") as articles_file:
        wikipedia_articles = load(articles_file)

    #flatten dictionary
    ARTICLES = [article for values in wikipedia_articles.values() for article in values]

    #scrape first five revisions of each article
    logger.start("Testing multiscraping " + ", ".join(ARTICLES) + "...")
    for article in ARTICLES:
        with Scraper(logger = LOGGER, title = article, language = "en") as scraper:
            scraper.scrape(DIRECTORY, html=False, number=5)
    logger.stop("Multiscraping test successful.", 1)

def test_pipeline(logger):
    DIRECTORY = ".." + sep + "test" + sep + "test_pipeline"
    FILEPATH = DIRECTORY + sep + FILENAME

    logger.start("Testing pipeline...")
    
    #scrape article
    with Scraper(logger = logger, title = TITLE, language = LANGUAGE) as scraper:
        scraper.scrape(DIRECTORY, html=False)

    article = Article(FILEPATH)
    article.plot_revision_distribution_to_file(DIRECTORY)

    #load bibliography
    bibliography = Bibliography(".." + sep + "data" + sep + "Referenzen_crispr_cas.csv").from_csv()
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

def test_bibentry_conversion(logger):

    logger.start("Testing bibentry conversion...")
    
    bibentry = Bibentry(("WOS:0123456789	" + \
                        "UNNECESSARY LONG TITLE & IT HAS A WEIRD CHARACTER	" + \
                        "SURNAME,FN.	" + \
                        "A PUBLISHER	" + \
                        "15	" + \
                        "25	" + \
                        "42	" + \
                        "151	" + \
                        "2005	" + \
                        "00.1111/FOO.0.11111-2").split("\t"))
    bibentry_as_pprint = str(bibentry)
    print(bibentry_as_pprint)

    #sanity-check bibentry pprint
    assert bibentry_as_pprint == \
           "{'author': {'firstname': 'Fn.',\n" + \
           "            'fullname': 'Surname,Fn.',\n" + \
           "            'surname': 'Surname'},\n" + \
           " 'doi': '00.1111/foo.0.11111-2',\n" + \
           " 'issue': '42',\n" + \
           " 'page_end': '25',\n" + \
           " 'page_start': '15',\n" + \
           " 'source': 'a publisher',\n" + \
           " 'title': 'unnecessary long title & it has a weird character',\n" + \
           " 'volume': '151',\n" + \
           " 'wos': 'wos:0123456789',\n" + \
           " 'year': 2005}"

    bibentry_as_bibtex = str(bibentry.bibtex())
    print(bibentry_as_bibtex)

    #sanity-check bibentry bibtext
    assert bibentry_as_bibtex == \
           "{'wos': 'wos:0123456789', " + \
           "'title': 'unnecessary long title & it has a weird character', " + \
           "'author': 'Surname,Fn.', " + \
           "'source': 'a publisher', " + \
           "'issue': '42', " + \
           "'volume': '151', " + \
           "'year': 2005, " + \
           "'doi': '00.1111/foo.0.11111-2', " + \
           "'pages': '15-25'}"

    logger.stop("Bibentry conversion test successfull.", 1)

def test_bibliography_conversion(logger):
    DIRECTORY = ".." + sep + "test" + sep + "test_bibliography_conversion"
    FILENAME = "Referenzen_crispr_cas.bib"
    FILEPATH = DIRECTORY + sep + FILENAME

    logger.start("Testing bibliography conversion...")

    #load bibliography csv and covert to BibTex
    bibliography_csv = Bibliography(".." + sep + "data" + sep + "Referenzen_crispr_cas.csv").from_csv()
    bibliography_csv.write_bibtex_file(FILEPATH)


    logger.stop("Bibliography conversion test successful.", 1)

with Logger(".." + sep + "test" + sep + "logs") as LOGGER:
##    test_full_and_updated_scrape(LOGGER)
##    test_multi_scrape_with_5_revisions(LOGGER)
##    test_pipeline(LOGGER)
##    test_bibentry_conversion(LOGGER)
    test_bibliography_conversion(LOGGER)
