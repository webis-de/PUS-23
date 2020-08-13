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

    logger.stop("Singlescraping test finished.", 1)

    #assert full and update scrape match
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
    logger.start("Testing multiscraping " + ", ".join(ARTICLES) + "...")
    for article in ARTICLES:
        with Scraper(logger = LOGGER, title = article, language = "en") as scraper:
            scraper.scrape(DIRECTORY, html=False, number=5)
    logger.stop("Multiscraping test finished.", 1)

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
    bibliography = Bibliography(".." + sep + "data" + sep + "Referenzen_crispr_cas.csv")
    bibliography.plot_publication_distribution_to_file(DIRECTORY)

    #track bibkeys and print/plot
    tracks = article.track_bibkeys_in_article(["titles", "dois", "authors"], bibliography)
    for track in tracks.items():
        article.write_track_to_file(track, DIRECTORY)
        article.plot_track_to_file(track, DIRECTORY)

    logger.stop("Pipeline test finished.", 1)

    #assert revision information
    assert article.revisions[0].revid == 69137443
    assert article.revisions[0].timestamp.string == "2010-01-11 02:11:54"
    assert article.revisions[0].user == "Tinz"
    assert article.revisions[0].userid == 92881
    assert article.revisions[0].comment == "neu, wird noch erweitert"

def test_bibentry_conversion(logger):

    logger.start("Testing bibentry conversion...")
    
    bibentry = Bibentry(("WOS:000227707100005	" + \
                        "CRISPR ELEMENTS IN YERSINIA PESTIS	" + \
                        "POURCEL,C	" + \
                        "MICROBIOLOGY-SGM	" + \
                        "653	" + \
                        "663	" + \
                        "	" + \
                        "151	" + \
                        "2005	" + \
                        "10.1099/MIC.0.27437-0").split("\t"))
    bibentry_as_pprint = str(bibentry)
    bibentry_as_bibtex = bibentry.to_bibtex()

    logger.stop("Bibentry conversion test finished.", 1)

    #sanity-check bibentry pprint
    assert bibentry_as_pprint == \
           "{'author': {'firstname': 'C',\n" + \
           "            'fullname': 'POURCEL,C',\n" + \
           "            'names': ['POURCEL', 'C'],\n" + \
           "            'surname': 'Pourcel'},\n" + \
           " 'doi': '10.1099/mic.0.27437-0',\n" + \
           " 'issue': '',\n" + \
           " 'page_end': '663',\n" + \
           " 'page_start': '653',\n" + \
           " 'source': 'microbiology-sgm',\n" + \
           " 'title': 'crispr elements in yersinia pestis',\n" + \
           " 'volume': '151',\n" + \
           " 'wos': 'wos:000227707100005',\n" + \
           " 'year': 2005}"

    #sanity-check bibentry bibtext
    assert bibentry_as_bibtex == \
           "@article{pourcel:2005,\n" + \
           "	wos    = {wos:000227707100005},\n" + \
           "	title  = {crispr elements in yersinia pestis},\n" + \
           "	author = {Pourcel, C},\n" + \
           "	source = {microbiology-sgm},\n" + \
           "	issue  = {},\n" + \
           "	volume = {151},\n" + \
           "	year   = {2005},\n" + \
           "	doi    = {10.1099/mic.0.27437-0},\n" + \
           "	pages  = {653-663}\n" + \
           "}\n"

def test_bibliography_conversion(logger):
    DIRECTORY = ".." + sep + "test" + sep + "test_bibliography_conversion"
    FILENAME = "Referenzen_crispr_cas.bib"
    FILEPATH = DIRECTORY + sep + FILENAME

    logger.start("Testing bibliography conversion...")

    #load bibliography csv and covert to BibTex
    bibliography = Bibliography(".." + sep + "data" + sep + "Referenzen_crispr_cas.csv")
    bibliography.write_bibtex_file(FILEPATH)

    logger.stop("Bibliography conversion test finished.", 1)

with Logger(".." + sep + "test" + sep + "logs") as LOGGER:
    test_full_and_updated_scrape(LOGGER)
    test_multi_scrape_with_5_revisions(LOGGER)
    test_pipeline(LOGGER)
    test_bibentry_conversion(LOGGER)
    test_bibliography_conversion(LOGGER)
