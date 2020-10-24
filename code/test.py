from scraper.scraper import Scraper
from entity.article import Article
from entity.revision.revision import Revision
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

def mock_save(directory, revision):
    directory += [revision]

def mock_delay():
    return 0

def sorted_dictionary(dictionary):
    return {key:dictionary[key] for key in sorted(list(dictionary.keys()))}

def test_single_scrape(logger):
    logger.start("Testing single scrape")

    #scrape first five revisions
    logger.start_check("Singlescraping...")
    with Scraper(logger = logger, title = TITLE, language = LANGUAGE) as scraper:
        scraper.save = mock_save
        scraper.deley = mock_delay
        revisions = []
        scraper.scrape(revisions, number=5)
        revisions = [Revision(**revision) for revision in revisions]

        #assert attributes of first revision
        assert revisions[0].revid == 69137443
        assert revisions[0].parentid == 0
        assert "Cas-Komplexes in Einzelteile zerlegt" in revisions[0].get_text()
        assert revisions[0].user == "Tinz"
        assert revisions[0].timestamp == '2010-01-11T02:11:54Z'
        assert revisions[0].index == 0

        #assert attributes of fifth revision
        assert revisions[4].revid == 71287221
        assert revisions[4].parentid == 70862725
        assert "Cas-Komplexes (Cascade) in Einzelteile zerlegt" in revisions[4].get_text()
        assert revisions[4].user == "Hydro"
        assert revisions[4].timestamp == '2010-03-01T09:04:35Z'
        assert revisions[4].index == 4

    logger.stop("Single scrape test successful.", 1)

def test_multi_scrape(logger):
    #ARTICLE CHECKSUMS
    ARTICLES = {"CRISPR":"3b3b515988600fbddcd3a3d7b6a797da5dbe9381dd438d471ab2d86ad3bb0633",
                "CRISPR gene editing":"8e349f28a0e158c28d395ceb8c1beaf94b133e3686a25c366e6009e47f552661",
                "Cas9":"fec5eeab10e0f58be1d4460dd972783e7167652683175d5e3f50e4816a22fc83",
                "Trans-activating crRNA":"119a20105a7d64d95dc6606095ab58b7bb3584f2d16e2b17e5889f65194a0013",
                "CRISPR/Cpf1":"3f94f9c7ebcf0200f3d84e3032da5af19271b957b3f1e4192a4b66b3651a9c72"}
    
    #scrape first five revisions of each article and assert checksum code state 24 September 2020
    logger.start("Testing multiscraping " + ", ".join(ARTICLES) + "...")
    for article in ARTICLES:
        with Scraper(logger = LOGGER, title = article, language = "en") as scraper:
            scraper.save = mock_save
            scraper.delay = mock_delay
            revisions = []
            scraper.scrape(revisions, number=5)
            revisions = [Revision(**revision) for revision in revisions]
            checksum = revisions_checksum(revisions)
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
        scraper.delay = mock_delay
        scraper.scrape(DIRECTORY, number=3)
        number_of_full_scraped_revisions = scraper.revision_count
    full_scrape_file_checksum = file_checksum(FILEPATH)
    full_article = Article(FILEPATH)
    full_article.get_revisions()
    full_article_revisions_checksum = revisions_checksum(full_article.revisions)
    assert full_article.revisions[0].index == 0
    assert full_article.revisions[1].index == 1
    assert full_article.revisions[2].index == 2
    remove(FILEPATH)
    logger.end_check("Done.")

    #scrape first five revisions
    logger.start_check("Singlescraping (update)...")
    with Scraper(logger = logger, title = TITLE, language = LANGUAGE) as scraper:
        scraper.delay = mock_delay
        scraper.scrape(DIRECTORY, number=1)
    #scrape remaining revisions
    with Scraper(logger = logger, title = TITLE, language = LANGUAGE) as scraper:
        scraper.delay = mock_delay
        scraper.scrape(DIRECTORY, number=3)
        number_of_updated_scraped_revisions = scraper.revision_count
    update_scrape_file_checksum = file_checksum(FILEPATH)
    update_article = Article(FILEPATH)
    update_article.get_revisions()
    update_scrape_revisions_checksum = revisions_checksum(update_article.revisions)
    assert update_article.revisions[0].index == 0
    assert update_article.revisions[1].index == 1
    assert update_article.revisions[2].index == 2
    logger.end_check("Done.")

    #assert full and updated scrape match
    assert full_scrape_file_checksum == update_scrape_file_checksum
    assert full_article_revisions_checksum == update_scrape_revisions_checksum
    assert number_of_full_scraped_revisions == number_of_updated_scraped_revisions

    rmtree(DIRECTORY)

    logger.stop("Full and updated scrape test successful.", 1)

def test_pipeline(logger): #deprecated
    DIRECTORY = TEST_DIRECTORY + sep + "test_pipeline"

    assert not exists(DIRECTORY)
    
    FILEPATH = DIRECTORY + sep + FILENAME

    logger.start("Testing pipeline...")
    
    #scrape article
    with Scraper(logger = logger, title = TITLE, language = LANGUAGE) as scraper:
        scraper.scrape(DIRECTORY)

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
##        test_single_scrape(LOGGER)
##        test_multi_scrape(LOGGER)
        test_full_and_updated_scrape(LOGGER)
