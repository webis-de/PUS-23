from article.revision.source import Source
from lxml import html
import unittest

class TestSource(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        #Reference with title in quotation marks.
        cls.SOURCE1 = '<li id="cite_note-Groenen1993-24"><span class="mw-cite-backlink"><b><a href="#cite_ref-Groenen1993_24-0">^</a></b></span> ' + \
                      '<span class="reference-text"><cite id="CITEREFGroenenBunschotenvan_Soolingenvan_Embden1993" ' + \
                      'class="citation journal cs1">Groenen PM, Bunschoten AE, van Soolingen D, van Emden JD (1993). ' + \
                      '"Nature of DNA polymorphism in the direct repeat cluster of Mycobacterium tuberculosis; ' + \
                      'application for strain differentiation by a novel typing method". <i>Molecular Microbiology</i> (10): 1057&#8211;65. ' + \
                      '<a href="/wiki/Doi_(identifier)" class="mw-redirect" title="Doi (identifier)">doi</a>:' + \
                      '<a rel="nofollow" class="external text" href="https://doi.org/10.1111%2Fj.1365-2958.1993.tb00976.x">10.1111/j.1365-2958.1993.tb00976.x</a>. ' + \
                      '<a href="/wiki/PMID_(identifier)" class="mw-redirect" title="PMID (identifier)">PMID</a>&#160;' + \
                      '<a rel="nofollow" class="external text" href="//pubmed.ncbi.nlm.nih.gov/7934856">7934856</a>.</cite><span'

        #Reference with title without quotation marks, PMID spaced and followed by letters, names with 'et al.', first names abbreviated with '.' and separated by ';' instead of ','
        cls.SOURCE2 = '<li id="cite_note-Groenen1993-24"><span class="mw-cite-backlink"><b><a href="#cite_ref-Groenen1993_24-0">^</a></b></span> ' + \
                      '<span class="reference-text"><cite id="CITEREFGroenenBunschotenvan_Soolingenvan_Embden1993" ' + \
                      'class="citation journal cs1">Groenen PM; Bunschoten AE, van Soolingen D. et al. (1993). ' + \
                      'Nature of DNA polymorphism in the direct repeat cluster of Mycobacterium tuberculosis; ' + \
                      'application for strain differentiation by a novel typing method. <i>Molecular Microbiology</i> (10): 1057&#8211;65. ' + \
                      'a wild doi appears 10.1111/j.1365-2958.1993.tb00976.x. ' + \
                      '<a href="/wiki/PMID_(identifier)" class="mw-redirect" title="PMID (identifier)">PMID</a>&#160;' + \
                      '<a rel="nofollow" class="external text" href="//pubmed.ncbi.nlm.nih.gov/7934856">     7934856FOOBAR</a>.</cite><span'     

    def test_text(self):    
        source = Source(html.fromstring(self.SOURCE1), 24)
        text = source.get_text()
        self.assertEqual(text, ('Groenen PM, Bunschoten AE, van Soolingen D, van Emden JD (1993). '
                                '"Nature of DNA polymorphism in the direct repeat cluster of Mycobacterium tuberculosis; '
                                'application for strain differentiation by a novel typing method". '
                                'Molecular Microbiology (10): 1057–65. doi:10.1111/j.1365-2958.1993.tb00976.x. PMID 7934856.'))

        source = Source(html.fromstring(self.SOURCE2), 24)
        text = source.get_text()
        self.assertEqual(text, ('Groenen PM; Bunschoten AE, van Soolingen D. et al. (1993). '
                                'Nature of DNA polymorphism in the direct repeat cluster of Mycobacterium tuberculosis; '
                                'application for strain differentiation by a novel typing method. '
                                'Molecular Microbiology (10): 1057–65. a wild doi appears 10.1111/j.1365-2958.1993.tb00976.x. PMID      7934856FOOBAR.'))
        
    def test_get_title(self):
        for SOURCE in [self.SOURCE1, self.SOURCE2]:
            source = Source(html.fromstring(SOURCE), 24)
            title = source.get_title("en")
            self.assertEqual(title, ("Nature of DNA polymorphism in the direct repeat cluster of Mycobacterium tuberculosis; "
                                     "application for strain differentiation by a novel typing method"))

    def test_get_authors(self):    
        source = Source(html.fromstring(self.SOURCE1), 24)
        authors = source.get_authors("en")
        self.assertEqual(authors, [('Groenen', 'PM'), ('Bunschoten', 'AE'), ('van Soolingen', 'D'), ('van Emden', 'JD')])

        source = Source(html.fromstring(self.SOURCE2), 24)
        authors = source.get_authors("en")
        self.assertEqual(authors, [('Groenen', 'PM'), ('Bunschoten', 'AE'), ('van Soolingen', 'D')])
        
    def test_get_dois(self):
        for SOURCE in [self.SOURCE1, self.SOURCE2]:
            source = Source(html.fromstring(SOURCE), 24)
            dois = source.get_dois()
            self.assertEqual(dois, ["10.1111/j.1365-2958.1993.tb00976.x"])
        
    def test_get_pmids(self):
        for SOURCE in [self.SOURCE1, self.SOURCE2]:
            source = Source(html.fromstring(SOURCE), 24)
            pmids = source.get_pmids()
            self.assertEqual(pmids, ["7934856"])
        
if __name__ == "__main__":
    unittest.main()
