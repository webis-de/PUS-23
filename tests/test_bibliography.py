from code.bibliography.bibliography import Bibliography
from os.path import sep
import unittest

class TestBibliography(unittest.TestCase):

    def test_bibliography(self):
        
        bibliography = Bibliography("data" + sep + "tracing-innovations-lit.bib")
        for bibentry in bibliography.bibentries.values():
            for author in bibentry.authors:
                try:
                    AUTHOR = ("\t" + author)
                except IndexError:
                    print(bibentry)
                AUTHOR = ("\t" + author)

if __name__ == "__main__":
    unittest.main()
