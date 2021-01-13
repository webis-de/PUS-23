from bibliography.bibliography import Bibliography
from os.path import sep
import unittest

class TestBibliography(unittest.TestCase):

    def test_bibliography(self):
        
        bibliography = Bibliography(".." + sep + "data" + sep + "tracing-innovations-lit.bib")
        for bibentry in bibliography.bibentries.values():
            for author in bibentry.persons.get("author"):
                try:
                    AUTHOR = ("\t" + author.last_names[0] + " " + author.first_names[0])
                except IndexError:
                    print(bibentry.to_string("bibtex"))
                AUTHOR = ("\t" + author.last_names[0] + " " + author.first_names[0])

    def test_replace_braces(self):

        bibliography = Bibliography(".." + sep + "data" + sep + "tracing-innovations-lit.bib")

        title = '{Identification of Genes that Are Associated with DNA Repeats in Prokaryotes}'
        persons = ['Jansen, Ruud', '{van Embden}, {Jan D. A.}', 'Gaastra, Wim', 'Schouls, {Leo M.}']

        self.assertEqual(bibliography.replace_braces(title), "Identification of Genes that Are Associated with DNA Repeats in Prokaryotes")
        self.assertEqual(bibliography.replace_braces(persons), ['Jansen, Ruud', 'van Embden, Jan D. A.', 'Gaastra, Wim', 'Schouls, Leo M.'])
        self.assertEqual(bibliography.replace_braces(tuple(persons[1].split(", "))),('van Embden', 'Jan D. A.'))

if __name__ == "__main__":
    unittest.main()
