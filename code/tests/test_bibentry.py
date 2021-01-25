from bibliography.bibentry import Bibentry
import unittest

class MockedBibentry:

    def __init__(self, doi):
        
        self.key = "foo:2000"
        self.fields = {"title":"",
                       "doi":doi,
                       "pmid":123456789,
                       "year":2000}
        self.persons = {"author":[]}

class TestBibentry(unittest.TestCase):

    def test_replace_braces(self):

        bibentry = Bibentry(MockedBibentry("foo"))

        title = '{Identification of Genes that Are Associated with DNA Repeats in Prokaryotes}'
        persons = ['Jansen, Ruud', '{van Embden}, {Jan D. A.}', 'Gaastra, Wim', 'Schouls, {Leo M.}']

        self.assertEqual(bibentry.replace_braces(title), "Identification of Genes that Are Associated with DNA Repeats in Prokaryotes")
        self.assertEqual(bibentry.replace_braces(persons), ['Jansen, Ruud', 'van Embden, Jan D. A.', 'Gaastra, Wim', 'Schouls, Leo M.'])
        self.assertEqual(bibentry.replace_braces(tuple(persons[1].split(", "))),('van Embden', 'Jan D. A.'))

    def test_doi_valid(self):

        bibentry = Bibentry(MockedBibentry("10.1111/j.1365-2958.1993.tb01721.x"))
        self.assertTrue(bibentry.doi_valid())
        bibentry = Bibentry(MockedBibentry("foo"))
        self.assertFalse(bibentry.doi_valid())
        

if __name__ == "__main__":
    unittest.main()
