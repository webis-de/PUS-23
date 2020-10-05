from scraper.scraper import Scraper
from entity.article import Article
from entity.bibliography import Bibliography
from utility.logger import Logger
from os import remove, rename, rmdir
from shutil import rmtree
from os.path import exists, sep
from hashlib import sha256

TEST_DIRECTORY = ".." + sep + "test"
TITLE = "CRISPR"
LANGUAGE = "de"
FILENAME = TITLE + "_" + LANGUAGE

def file_checksum(filepath):
    sha256_hash = sha256()
    with open(filepath,"rb") as f:
        for byte_block in iter(lambda: f.read(4096),b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def revisions_checksum(revisions):
    sha256_hash = sha256()
    for revision in revisions:
        sha256_hash.update(str(revision.__dict__).encode("utf-8"))
    return sha256_hash.hexdigest()

def mock_save(r, d):
    pass

def sorted_dictionary(dictionary):
    return {key:dictionary[key] for key in sorted(list(dictionary.keys()))}

def test_single_scrape(logger):
    DIRECTORY = TEST_DIRECTORY + sep + "test_single_scrape"
    FILEPATH = DIRECTORY + sep + FILENAME
    logger.start("Testing single scrape")

    #scrape first five revisions
    logger.start_check("Singlescraping...")
    with Scraper(logger = logger, title = TITLE, language = LANGUAGE) as scraper:
        scraper.save = mock_save
        scraper.scrape(DIRECTORY, html=True, number=5)

        #assert attributes of first revision
        assert scraper.revisions[0].revid == 69137443
        assert scraper.revisions[0].parentid == 0
        assert "Cas-Komplexes in Einzelteile zerlegt" in scraper.revisions[0].get_text()
        assert scraper.revisions[0].user == "Tinz"
        assert scraper.revisions[0].timestamp == '2010-01-11T02:11:54Z'

        #assert attributes of fifth revision
        assert scraper.revisions[4].revid == 71287221
        assert scraper.revisions[4].parentid == 70862725
        assert "Cas-Komplexes (Cascade) in Einzelteile zerlegt" in scraper.revisions[4].get_text()
        assert scraper.revisions[4].user == "Hydro"
        assert scraper.revisions[4].timestamp == '2010-03-01T09:04:35Z'

    logger.stop("Single scrape test successful.", 1)

def test_multi_scrape(logger):
    DIRECTORY = TEST_DIRECTORY + sep + "test_multi_scrape"

    #ARTICLE CHECKSUMS WITHOUT HTML
    ARTICLES = {"CRISPR":"ec49dd32946f736efdf7d3db050eb53a0178d1dc0a8c7ed3bf8db3766d57a1cc",
                "CRISPR gene editing":"bdca90e56f4b0ad1e4d499c7ffb62d71527397801fb57d2a0c55565131515ad4",
                "Cas9":"73b570cf10160b610220bc335c11a1e9a634a282e6a2b724be65e2aba6491f07",
                "Trans-activating crRNA":"020206c191da8b5aca210b8dcb8eea960fb9199ebc6046592cfef68c81398594",
                "CRISPR/Cpf1":"f8797c9fb37ae10898a62b729b69cd2ca91ed5229c0e954598a896d0ea1e8a67"}
    #ARTICLE CHECKSUMS WITH HTML
    ARTICLES = {"CRISPR":"3b3b515988600fbddcd3a3d7b6a797da5dbe9381dd438d471ab2d86ad3bb0633",
                "CRISPR gene editing":"1da367d5705c2b9e926fbabbbc1bc1c515ab82dc0bb694268e78cb52b83cd3ba",
                "Cas9":"fec5eeab10e0f58be1d4460dd972783e7167652683175d5e3f50e4816a22fc83",
                "Trans-activating crRNA":"ba7dc144f7610f28ec032b13e5ea759f8bc5cba20095124bee4baac8f49fd6dd",
                "CRISPR/Cpf1":"e60a7b281fecb0f9f494d85245ad03864cc94a5b124439bf05084c09c1c963ee"}
    
    #scrape first five revisions of each article and assert checksum code state 24 September 2020
    logger.start("Testing multiscraping " + ", ".join(ARTICLES) + "...")
    for article in ARTICLES:
        with Scraper(logger = LOGGER, title = article, language = "en") as scraper:
            scraper.save = mock_save
            scraper.scrape(DIRECTORY, html=True, number=5)
            checksum = revisions_checksum(scraper.revisions)
            assert checksum == ARTICLES[article]
    logger.stop("Multiscraping test successful.", 1)

def test_full_and_updated_scrape(logger):    
    DIRECTORY = TEST_DIRECTORY + sep + "test_full_and_updated_scrape"

    assert not exists(DIRECTORY)
    
    FILEPATH = DIRECTORY + sep + FILENAME

    logger.start("Testing full and updated scrape")

    #scrape article in full
    logger.start_check("Singlescraping (full)...")
    with Scraper(logger = logger, title = TITLE, language = LANGUAGE) as scraper:
        scraper.scrape(DIRECTORY, html=True)
        number_of_full_scraped_revisions = scraper.revision_count
    full_scrape_checksum = file_checksum(FILEPATH)
    remove(FILEPATH)
    logger.end_check("Done.")

    #scrape first five revisions
    logger.start_check("Singlescraping (update)...")
    with Scraper(logger = logger, title = TITLE, language = LANGUAGE) as scraper:
        scraper.scrape(DIRECTORY, html=True, number=5)
    #scrape remaining revisions
    with Scraper(logger = logger, title = TITLE, language = LANGUAGE) as scraper:
        scraper.scrape(DIRECTORY, html=True)
        number_of_updated_scraped_revisions = scraper.revision_count
    update_scrape_checksum = file_checksum(FILEPATH)
    logger.end_check("Done.")

    #assert full and updated scrape match
    assert full_scrape_checksum == update_scrape_checksum
    assert number_of_full_scraped_revisions == number_of_updated_scraped_revisions

    rmtree(DIRECTORY)

    logger.stop("Full and updated scrape test successful.", 1)

def test_pipeline(logger):
    DIRECTORY = TEST_DIRECTORY + sep + "test_pipeline"

    assert not exists(DIRECTORY)
    
    FILEPATH = DIRECTORY + sep + FILENAME

    logger.start("Testing pipeline...")
    
    #scrape article
    with Scraper(logger = logger, title = TITLE, language = LANGUAGE) as scraper:
        scraper.scrape(DIRECTORY, html=True)

    #load article from file
    article = Article(FILEPATH)
    article.plot_revision_distribution_to_file(DIRECTORY)

    #load bibliography from file
    bibliography = Bibliography(".." + sep + "data" + sep + "tracing-innovations-lit.bib")
    bibliography.plot_publication_distribution_to_file(DIRECTORY)

    #track bibkeys and print/plot
    tracks = article.track_field_values_in_article(["titles", "dois", "authors"], bibliography)
    for track in tracks.items():
        article.write_track_to_file(track, DIRECTORY)
        article.plot_track_to_file(track, DIRECTORY)

    #assert revision information
    assert article.revisions[0].revid == 69137443
    assert article.revisions[0].timestamp_pretty_string() == "2010-01-11 02:11:54"
    assert article.revisions[0].user == "Tinz"
    assert article.revisions[0].userid == 92881
    assert article.revisions[0].comment == "neu, wird noch erweitert"

    rmtree(DIRECTORY)

    logger.stop("Pipeline test successful.", 1)

if __name__ == "__main__":     
    
    with Logger(TEST_DIRECTORY) as LOGGER:
        test_single_scrape(LOGGER)
        test_multi_scrape(LOGGER)
        test_full_and_updated_scrape(LOGGER)
        test_pipeline(LOGGER)
