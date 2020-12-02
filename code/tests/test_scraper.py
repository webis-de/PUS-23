from scraper.scraper import Scraper
from utility.logger import Logger
from article.article import Article
from article.revision.revision import Revision
from os import remove
from os.path import exists, sep
from shutil import rmtree
from hashlib import sha256
import unittest

class TestSraper(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.directory = "tests" + sep + "scraper_test_directory"
        cls.log_directory = cls.directory + sep + "log"
        cls.data_directory = cls.directory + sep + "data"
        cls.logger = Logger(cls.log_directory)

    @classmethod
    def tearDownClass(cls):
        rmtree(cls.directory)

    def file_checksum(self, filepath):
        sha256_hash = sha256()
        with open(filepath,"rb") as f:
            for byte_block in iter(lambda: f.read(4096),b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()

    def revisions_checksum(self, revisions):
        sha256_hash = sha256()
        for revision in revisions:
            revision.timestamp = revision.timestamp.datetime.strftime("%Y-%m-%dT%H:%M:%SZ")
            sha256_hash.update(str(revision.__dict__).encode("utf-8"))
        return sha256_hash.hexdigest()

    def mock_save(self, directory, revision):
        directory += [revision]

    def mock_delay(self):
        return 0

    def mock_log(self, message, line_breaks = 0):
        pass

    def test_single_scrape(self):
        TITLE = "CRISPR"
        LANGUAGE = "de"
        DEADLINE = "2010-03-02"

        self.logger.log = self.mock_log

        #scrape first five revisions
        with Scraper(logger = self.logger, title = "CRISPR", language = LANGUAGE) as scraper:
            scraper.save = self.mock_save
            scraper.delay = self.mock_delay
            revisions = []
            scraper.scrape(revisions, DEADLINE, verbose=False)
            revisions = [Revision(**revision) for revision in revisions]

            #assert attributes of first revision
            self.assertEqual(revisions[0].revid, 69137443)
            self.assertEqual(revisions[0].parentid, 0)
            self.assertIn("Cas-Komplexes in Einzelteile zerlegt", revisions[0].get_text())
            self.assertEqual(revisions[0].user, "Tinz")
            self.assertEqual(revisions[0].timestamp.string, '2010-01-11 02:11:54')
            self.assertEqual(revisions[0].index, 0)

            #assert attributes of fifth revision
            self.assertEqual(revisions[-1].revid, 71287221)
            self.assertEqual(revisions[-1].parentid, 70862725)
            self.assertIn("Cas-Komplexes (Cascade) in Einzelteile zerlegt", revisions[4].get_text())
            self.assertEqual(revisions[-1].user, "Hydro")
            self.assertEqual(revisions[-1].timestamp.string, '2010-03-01 09:04:35')
            self.assertEqual(revisions[-1].index, 4)

    def test_multi_scrape(self):
        LANGUAGE = "en"
        DEADLINE = "2020-10-25"

        self.logger.log = self.mock_log
        
        #ARTICLE CHECKSUMS
        ARTICLES = {"CRISPR":"3b3b515988600fbddcd3a3d7b6a797da5dbe9381dd438d471ab2d86ad3bb0633",
                    "CRISPR gene editing":"8e349f28a0e158c28d395ceb8c1beaf94b133e3686a25c366e6009e47f552661",
                    "Cas9":"fec5eeab10e0f58be1d4460dd972783e7167652683175d5e3f50e4816a22fc83",
                    "Trans-activating crRNA":"119a20105a7d64d95dc6606095ab58b7bb3584f2d16e2b17e5889f65194a0013",
                    "CRISPR/Cpf1":"3f94f9c7ebcf0200f3d84e3032da5af19271b957b3f1e4192a4b66b3651a9c72"}
        
        #scrape first five revisions of each article and assert checksum code state 24 September 2020
        for article in ARTICLES:
            with Scraper(logger = self.logger, title = article, language = LANGUAGE) as scraper:
                scraper.save = self.mock_save
                scraper.delay = self.mock_delay
                revisions = []
                scraper.scrape(revisions, DEADLINE, number=5, verbose=False)
                revisions = [Revision(**revision) for revision in revisions]
                checksum = self.revisions_checksum(revisions)
                self.assertEqual(checksum, ARTICLES[article])

    def test_full_and_updated_scrape(self):
        TITLE = "CRISPR"
        LANGUAGE = "en"
        DEADLINE = "2020-10-25"

        self.logger.log = self.mock_log
        
        self.assertFalse(exists(self.data_directory), msg="Last test run aborted, please remove directory: " + self.data_directory)
        
        FILEPATH = self.data_directory + sep + TITLE + "_" + LANGUAGE

        #scrape article in full
        with Scraper(logger = self.logger, title = TITLE, language = LANGUAGE) as scraper:
            scraper.delay = self.mock_delay
            scraper.scrape(self.data_directory, DEADLINE, number=15, verbose=False)
            number_of_full_scraped_revisions = scraper.revision_count
        full_scrape_file_checksum = self.file_checksum(FILEPATH)
        full_article = Article(FILEPATH)
        full_article.get_revisions()
        full_article_revisions_checksum = self.revisions_checksum(full_article.revisions)
        self.assertEqual(full_article.revisions[0].index, 0)
        self.assertEqual(full_article.revisions[7].index, 7)
        self.assertEqual(full_article.revisions[14].index, 14)
        remove(FILEPATH)
        
        #scrape first five revisions
        with Scraper(logger = self.logger, title = TITLE, language = LANGUAGE) as scraper:
            scraper.delay = self.mock_delay
            scraper.scrape(self.data_directory, DEADLINE, number=10, verbose=False)
        #scrape remaining revisions
        with Scraper(logger = self.logger, title = TITLE, language = LANGUAGE) as scraper:
            scraper.delay = self.mock_delay
            scraper.scrape(self.data_directory, DEADLINE, number=15, verbose=False)
            number_of_updated_scraped_revisions = scraper.revision_count
        update_scrape_file_checksum = self.file_checksum(FILEPATH)
        update_article = Article(FILEPATH)
        update_article.get_revisions()
        update_scrape_revisions_checksum = self.revisions_checksum(update_article.revisions)
        self.assertEqual(update_article.revisions[0].index, 0)
        self.assertEqual(update_article.revisions[11].index, 11)
        self.assertEqual(update_article.revisions[14].index, 14)

        self.assertEqual(full_article_revisions_checksum, update_scrape_revisions_checksum)

        #assert full and updated scrape match
        self.assertEqual(full_scrape_file_checksum, update_scrape_file_checksum)
        self.assertEqual(full_article_revisions_checksum, update_scrape_revisions_checksum)
        self.assertEqual(number_of_full_scraped_revisions, number_of_updated_scraped_revisions)

if __name__ == "__main__":
    unittest.main()
