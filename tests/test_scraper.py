from code.scraper.scraper import Scraper
from code.utility.logger import Logger
from code.article.article import Article
from code.article.revision.revision import Revision
from os import remove
from os.path import exists, sep
from shutil import rmtree
from hashlib import sha256
import unittest
import logging

class TestScraper(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.directory = "tests" + sep + "scraper_test_directory"
        cls.no_title = "ABA)=$)!"
        logging.disable(logging.CRITICAL)
        
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

    def mock_latest_revid(self, filepath):
        return filepath

    def test_quote_and_unquote_filename(self):

        TITLE = "CRISPR/Cpf1 gene-editing"
        QUOTED = "CRISPR%2FCpf1_gene-editing_en"

        with Scraper(directory = self.directory, title = self.no_title, language = "en") as scraper:
            quoted_filename = scraper._quote_filename(TITLE)
            self.assertEqual(quoted_filename, QUOTED)

        with Scraper(directory = self.directory, title = self.no_title, language = "en") as scraper:
            unquoted_filename = scraper._unquote_filename(QUOTED)
            self.assertEqual(unquoted_filename, TITLE)

    def test_sanity_check(self):

        with Scraper(directory = self.directory, title = self.no_title, language = "en") as scraper:
            sanity_checked_title = scraper._sanity_check("Crispr")
            self.assertEqual(sanity_checked_title, "CRISPR")

    def test_rvstartid(self):        
        with Scraper(directory = self.directory, title = "CRISPR/Cas Tools", language = "en") as scraper:
            scraper._save = self.mock_save
            scraper._delay = self.mock_delay
            scraper._latest_revid = self.mock_latest_revid
            scraper._rvstartid("646367059")
        self.assertEqual(scraper.parameters["rvstartid"], "653185393")

    def test_before(self):
        with Scraper(directory = self.directory, title = self.no_title, language = "en") as scraper:
            self.assertTrue(scraper._before("2000-10-20T15:00:00Z", "2000-10-21"))
            self.assertTrue(scraper._before("2000-09-22T15:00:00Z", "2000-10-21"))
            self.assertTrue(scraper._before("1999-11-22T15:00:00Z", "2000-10-21"))

    def test_wikitext(self):

        wikitext = ("CRISPR are direct repeats found in the [[DNA]] of many [[bacteria]] and [[archaea]]. " +
                    "The name is an acronym for clustered regularly interspaced short palindromic repeats. " +
                    "These repeats range in size from 21 to 37 base pairs. They are separated by spacers of " +
                    "similar length. Spacers are usually unique in a genome. " +
                    "Different strains of the same species of bacterium can often be differentiated " +
                    "according to differences in the spacers in their CRISPR arrays, a technique called [[spoligotyping]].")

        #scrape first revision
        with Scraper(directory = self.directory, title = "CRISPR", language = "en") as scraper:
            scraper._save = self.mock_save
            scraper._delay = self.mock_delay
            revisions = []
            scraper.scrape(revisions, deadline="2005-07-01", number=1, verbose=False)
            revisions = [Revision(**revision) for revision in revisions]

            #assert Wikitext matches
            self.assertEqual(revisions[0].get_wikitext(), wikitext)

    def test_single_scrape(self):

        #scrape first five revisions
        with Scraper(directory = self.directory, title = "CRISPR/Cas Tools", language = "en") as scraper:
            scraper._save = self.mock_save
            scraper._delay = self.mock_delay
            revisions = []
            scraper.scrape(revisions, deadline="2015-02-15", number=5, verbose=False)
            revisions = [Revision(**revision) for revision in revisions]

            #assert number of revisions
            self.assertEqual(len(revisions), 5)

            #assert attributes of first revision
            self.assertEqual(revisions[0].revid, 645771291)
            self.assertEqual(revisions[0].parentid, 0)
            self.assertIn("The tools are presented on a table along with some of their key features.", revisions[0].get_text())
            self.assertEqual(revisions[0].user, "Cmvp")
            self.assertEqual(revisions[0].timestamp.string, '2015-02-05 17:01:49')
            self.assertEqual(revisions[0].index, 0)

            #assert attributes of fifth revision
            self.assertEqual(revisions[-1].revid, 646367059)
            self.assertEqual(revisions[-1].parentid, 645940725)
            self.assertIn("The below table lists available tools and their attributes, and includes links to the corresponding websites.", revisions[4].get_text())
            self.assertEqual(revisions[-1].user, "Cmvp")
            self.assertEqual(revisions[-1].timestamp.string, '2015-02-09 16:44:01')
            self.assertEqual(revisions[-1].index, 4)

    def test_redirect_scrape(self):
        TITLE = "Crispr"
        LANGUAGE = "en"
        DEADLINE = "2005-12-15"

        #scrape first five revisions
        with Scraper(directory = self.directory, title = TITLE, language = LANGUAGE) as scraper:
            scraper._save = self.mock_save
            scraper._delay = self.mock_delay
            revisions = []
            scraper.scrape(revisions, DEADLINE, verbose=False)
            revisions = [Revision(**revision) for revision in revisions]

            #assert number of revisions
            self.assertEqual(len(revisions), 6)

            #assert attributes of first revision
            self.assertEqual(revisions[0].revid, 17918488)
            self.assertEqual(revisions[0].parentid, 0)
            self.assertEqual(revisions[0].user, "192.207.234.194")
            self.assertEqual(revisions[0].timestamp.string, '2005-06-30 21:26:19')
            self.assertEqual(revisions[0].index, 0)

            #assert attributes of fifth revision
            self.assertEqual(revisions[-1].revid, 31074128)
            self.assertEqual(revisions[-1].parentid, 31073051)
            self.assertEqual(revisions[-1].user, "192.207.234.194")
            self.assertEqual(revisions[-1].timestamp.string, '2005-12-12 18:09:52')
            self.assertEqual(revisions[-1].index, 5)

    def test_multi_scrape(self):
        LANGUAGE = "en"
        DEADLINE = "2020-10-25"

        #ARTICLE METADATA
        ARTICLES = {"CRISPR":{"revid":31073051,"parentid":31072600,"timestamp":"2005-12-12 18:00"},
                    "CRISPR gene editing":{"revid":883728113,"parentid":883727959,"timestamp":"2019-02-17 06:39"},
                    "Cas9":{"revid":598617730,"parentid":597687410,"timestamp":"2014-03-07 23:25"},
                    "Trans-activating crRNA":{"revid":679103282,"parentid":626842992,"timestamp":"2015-09-02 13:20"},
                    "CRISPR/Cpf1":{"revid":693169731,"parentid":693169348,"timestamp":"2015-11-30 21:40"}}
        
        #scrape first five revisions of each article and assert checksum code state 24 September 2020
        for article in ARTICLES:
            with Scraper(directory = self.directory, title = article, language = LANGUAGE) as scraper:
                scraper._save = self.mock_save
                scraper._delay = self.mock_delay
                revisions = []
                scraper.scrape(revisions, DEADLINE, number=5, verbose=False)
                revisions = [Revision(**revision) for revision in revisions]
                self.assertEqual(revisions[4].revid, ARTICLES[article]["revid"])
                self.assertEqual(revisions[4].parentid, ARTICLES[article]["parentid"])
                self.assertEqual(revisions[4].timestamp.string[:-3], ARTICLES[article]["timestamp"])

    def test_full_and_updated_scrape(self):
        TITLE = "CRISPR gene editing"
        LANGUAGE = "en"
        DEADLINE = "2019-02-18"

        self.assertFalse(exists(self.directory + sep + "CRISPR gene editing"), msg="Last test run aborted, please remove directory: " + self.directory)

        #scrape article in full
        with Scraper(directory = self.directory, title = TITLE, language = LANGUAGE) as scraper:
            scraper._delay = self.mock_delay
            scraper.scrape(self.directory, DEADLINE, number=15, verbose=False)
            number_of_full_scraped_revisions = scraper.revision_count
            FILEPATH = self.directory + sep + scraper.filename
            
        full_scrape_file_checksum = self.file_checksum(FILEPATH)
        full_article = Article(FILEPATH)
        full_article.get_revisions()
        full_article_revisions_checksum = self.revisions_checksum(full_article.revisions)
        self.assertEqual(full_article.revisions[0].index, 0)
        self.assertEqual(full_article.revisions[7].index, 7)
        self.assertEqual(full_article.revisions[14].index, 14)
        remove(FILEPATH)
        
        #scrape first five revisions
        with Scraper(directory = self.directory, title = TITLE, language = LANGUAGE) as scraper:
            scraper._delay = self.mock_delay
            scraper.scrape(self.directory, DEADLINE, number=10, verbose=False)
        #scrape remaining revisions
        with Scraper(directory = self.directory, title = TITLE, language = LANGUAGE) as scraper:
            scraper._delay = self.mock_delay
            scraper.scrape(self.directory, DEADLINE, number=15, verbose=False)
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
