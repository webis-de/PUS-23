from code.bibliography.bibentry import Bibentry
import unittest

class TestBibentry(unittest.TestCase):

    def test_doi_valid(self):

        bibentry = Bibentry("mojica:1993", {"title":"",
                                         "authors":[],
                                         "doi":"10.1111/j.1365-2958.1993.tb01721.x",
                                         "pmid":"",
                                         "year":"1993"})
        self.assertTrue(bibentry.doi_valid())
        bibentry = Bibentry("foo:2000", {"title":"",
                                         "authors":[],
                                         "doi":"foo",
                                         "pmid":123456789,
                                         "year":"2000"})
        self.assertFalse(bibentry.doi_valid())
        

if __name__ == "__main__":
    unittest.main()
