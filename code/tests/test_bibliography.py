from bibliography.bibliography import Bibliography
from os.path import sep
import unittest

class TestBibliography(unittest.TestCase):

    def test_bibliography(self):
        
        bibliography = Bibliography(".." + sep + "data" + sep + "tracing-innovations-lit.bib")
        for bibentry in bibliography.bibentries.values():
            for author in bibentry.authors:
                try:
                    AUTHOR = ("\t" + author)
                except IndexError:
                    print(bibentry)
                AUTHOR = ("\t" + author)

    def test_replace_braces(self):

        bibliography = Bibliography(".." + sep + "data" + sep + "tracing-innovations-lit.bib")

        title = '{Identification of Genes that Are Associated with DNA Repeats in Prokaryotes}'
        persons = ['Jansen, Ruud', '{van Embden}, {Jan D. A.}', 'Gaastra, Wim', 'Schouls, {Leo M.}']

        self.assertEqual(list(bibliography.bibentries.values())[0].replace_braces(title), "Identification of Genes that Are Associated with DNA Repeats in Prokaryotes")
        self.assertEqual(list(bibliography.bibentries.values())[0].replace_braces(persons), ['Jansen, Ruud', 'van Embden, Jan D. A.', 'Gaastra, Wim', 'Schouls, Leo M.'])
        self.assertEqual(list(bibliography.bibentries.values())[0].replace_braces(tuple(persons[1].split(", "))),('van Embden', 'Jan D. A.'))

if __name__ == "__main__":
    unittest.main()
