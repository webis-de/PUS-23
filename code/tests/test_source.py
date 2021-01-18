from article.revision.source import Source
from lxml import html
import unittest

class TestSource(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        #Reference with title in quotation marks.
        cls.html1 = ('<li id="cite_note-Groenen1993-24"><span class="mw-cite-backlink"><b><a href="#cite_ref-Groenen1993_24-0">^</a></b></span> '
                     '<span class="reference-text"><cite id="CITEREFGroenenBunschotenvan_Soolingenvan_Embden1993" '
                     'class="citation journal cs1">Groenen PM, Bunschoten AE, van Soolingen D, van Emden JD (1993). '
                     '"Nature of DNA polymorphism in the direct repeat cluster of Mycobacterium tuberculosis; '
                     'application for strain differentiation by a novel typing method". <i>Molecular Microbiology</i> (10): 1057&#8211;65. '
                     '<a href="/wiki/Doi_(identifier)" class="mw-redirect" title="Doi (identifier)">doi</a>:'
                     '<a rel="nofollow" class="external text" href="https://doi.org/10.1111%2Fj.1365-2958.1993.tb00976.x">10.1111/j.1365-2958.1993.tb00976.x</a>. '
                     '<a href="/wiki/PMID_(identifier)" class="mw-redirect" title="PMID (identifier)">PMID</a>&#160;'
                     '<a rel="nofollow" class="external text" href="//pubmed.ncbi.nlm.nih.gov/7934856">7934856</a>.</cite><span')
        cls.source1 = Source(html.fromstring(cls.html1))

        #Reference with title without quotation marks, PMID spaced and followed by letters, names with 'et al.', first names abbreviated with '.' and separated by ';' instead of ','
        cls.html2 = ('<li id="cite_note-Groenen1993-24"><span class="mw-cite-backlink"><b><a href="#cite_ref-Groenen1993_24-0">^</a></b></span> '
                     '<span class="reference-text"><cite id="CITEREFGroenenBunschotenvan_Soolingenvan_Embden1993" '
                     'class="citation journal cs1">Groenen PM; Bunschoten AE, van Soolingen D. et al. (1993). '
                     'Nature of DNA polymorphism in the direct repeat cluster of Mycobacterium tuberculosis; '
                     'application for strain differentiation by a novel typing method. <i>Molecular Microbiology</i> (10): 1057&#8211;65. '
                     'a wild doi appears 10.1111/j.1365-2958.1993.tb00976.x. '
                     '<a href="/wiki/PMID_(identifier)" class="mw-redirect" title="PMID (identifier)">PMID</a>&#160;'
                     '<a rel="nofollow" class="external text" href="//pubmed.ncbi.nlm.nih.gov/7934856">     7934856FOOBAR</a>.</cite><span')
        cls.source2 = Source(html.fromstring(cls.html2))

        #Reference with PMC
        cls.html3 = ('<li id="cite_note-pmid12032318-21"><span class="mw-cite-backlink"><b><a href="#cite_ref-pmid12032318_21-0" aria-label="Jump up" title="Jump up">^</a></b></span> '
                     '<span class="reference-text"><link rel="mw-deduplicated-inline-style" href="mw-data:TemplateStyles:r999302996"><cite id="CITEREFTang_TH,_Bachellerie_JP,_Rozhdestvensky_T,_Bortolin_ML,_Huber_H,_Drungowski_M2002" '
                     'class="citation journal cs1">Tang TH, Bachellerie JP, Rozhdestvensky T, Bortolin ML, Huber H, Drungowski M;  et&nbsp;al. (2002). '
                     '<a rel="nofollow" class="external text" href="https://www.ncbi.nlm.nih.gov/entrez/eutils/elink.fcgi?dbfrom=pubmed&amp;'
                     'tool=sumsearch.org/cite&amp;retmode=ref&amp;cmd=prlinks&amp;id=12032318">"Identification of 86 candidates for small non-messenger '
                     'RNAs from the archaeon Archaeoglobus fulgidus"</a>. <i>Proc Natl Acad Sci U S A</i>. <b>99</b> (11): 7536–41. '
                     '<a href="https://en.wikipedia.org/wiki/Bibcode_(identifier)" class="mw-redirect" title="Bibcode (identifier)">Bibcode</a>:<a rel="nofollow" '
                     'class="external text" href="https://ui.adsabs.harvard.edu/abs/2002PNAS...99.7536T">2002PNAS...99.7536T</a>. '
                     '<a href="https://en.wikipedia.org/wiki/Doi_(identifier)" class="mw-redirect" title="Doi (identifier)">doi</a>:'
                     '<a rel="nofollow" class="external text" href="https://doi.org/10.1073%2Fpnas.112047299">10.1073/pnas.112047299</a>. '
                     '<a href="https://en.wikipedia.org/wiki/PMC_(identifier)" class="mw-redirect" title="PMC (identifier)">PMC</a>&nbsp;'
                     '<span class="cs1-lock-free" title="Freely accessible"><a rel="nofollow" class="external text" href="https://www.ncbi.nlm.nih.gov/pmc/articles/PMC124276">124276</a></span>. '
                     '<a href="https://en.wikipedia.org/wiki/PMID_(identifier)" class="mw-redirect" title="PMID (identifier)">PMID</a>&nbsp;<a rel="nofollow" '
                     'class="external text" href="https://pubmed.ncbi.nlm.nih.gov/12032318">12032318</a>.</cite><span title="ctx_ver=Z39.88-2004&amp;'
                     'rft_val_fmt=info%3Aofi%2Ffmt%3Akev%3Amtx%3Ajournal&amp;rft.genre=article&amp;rft.jtitle=Proc+Natl+Acad+Sci+U+S+A&amp;'
                     'rft.atitle=Identification+of+86+candidates+for+small+non-messenger+RNAs+from+the+archaeon+Archaeoglobus+fulgidus.&amp;'
                     'rft.volume=99&amp;rft.issue=11&amp;rft.pages=7536-41&amp;rft.date=2002&amp;rft_id=%2F%2Fwww.ncbi.nlm.nih.gov%2Fpmc%2Farticles%2FPMC124276%23id-name%3DPMC&amp;'
                     'rft_id=info%3Apmid%2F12032318&amp;rft_id=info%3Adoi%2F10.1073%2Fpnas.112047299&amp;rft_id=info%3Abibcode%2F2002PNAS...99.7536T&amp;'
                     'rft.au=Tang+TH%2C+Bachellerie+JP%2C+Rozhdestvensky+T%2C+Bortolin+ML%2C+Huber+H%2C+Drungowski+M&amp;'
                     'rft_id=https%3A%2F%2Fwww.ncbi.nlm.nih.gov%2Fentrez%2Feutils%2Felink.fcgi%3Fdbfrom%3Dpubmed%26tool%3Dsumsearch.org%2Fcite%26retmode%3Dref%26cmd%3Dprlinks%26id%3D12032318&amp;'
                     'rfr_id=info%3Asid%2Fen.wikipedia.org%3ACRISPR" class="Z3988"></span><span class="cs1-maint citation-comment">'
                     'CS1 maint: multiple names: authors list (<a href="https://en.wikipedia.org/wiki/Category:CS1_maint:_multiple_names:_authors_list" title="Category:CS1 maint: multiple names: authors list">link</a>)</span> </span></li>')
        cls.source3 = Source(html.fromstring(cls.html3))

    def test_text(self):
        text = self.source1.get_text()
        self.assertEqual(text, ('Groenen PM, Bunschoten AE, van Soolingen D, van Emden JD (1993). '
                                '"Nature of DNA polymorphism in the direct repeat cluster of Mycobacterium tuberculosis; '
                                'application for strain differentiation by a novel typing method". '
                                'Molecular Microbiology (10): 1057–65. doi:10.1111/j.1365-2958.1993.tb00976.x. PMID 7934856.'))

        text = self.source2.get_text()
        self.assertEqual(text, ('Groenen PM; Bunschoten AE, van Soolingen D. et al. (1993). '
                                'Nature of DNA polymorphism in the direct repeat cluster of Mycobacterium tuberculosis; '
                                'application for strain differentiation by a novel typing method. '
                                'Molecular Microbiology (10): 1057–65. a wild doi appears 10.1111/j.1365-2958.1993.tb00976.x. PMID      7934856FOOBAR.'))

        text = self.source3.get_text()
        self.assertEqual(text, ('Tang TH, Bachellerie JP, Rozhdestvensky T, Bortolin ML, Huber H, Drungowski M;  et al. (2002). '
                                '"Identification of 86 candidates for small non-messenger RNAs from the archaeon Archaeoglobus fulgidus". '
                                'Proc Natl Acad Sci U S A. 99 (11): 7536–41. Bibcode:2002PNAS...99.7536T. doi:10.1073/pnas.112047299. PMC 124276. PMID 12032318.'))
        
    def test_get_title(self):
        self.assertEqual(self.source1.get_title("en"), ("Nature of DNA polymorphism in the direct repeat cluster of Mycobacterium tuberculosis; "
                                                        "application for strain differentiation by a novel typing method"))
        self.assertEqual(self.source2.get_title("en"), ("Nature of DNA polymorphism in the direct repeat cluster of Mycobacterium tuberculosis; "
                                                        "application for strain differentiation by a novel typing method"))
        self.assertEqual(self.source3.get_title("en"), ("Identification of 86 candidates for small non-messenger RNAs from the archaeon Archaeoglobus fulgidus"))

    def test_get_authors(self):    
        authors = self.source1.get_authors("en")
        self.assertEqual(authors, [('Groenen', 'PM'), ('Bunschoten', 'AE'), ('van Soolingen', 'D'), ('van Emden', 'JD')])

        authors = self.source2.get_authors("en")
        self.assertEqual(authors, [('Groenen', 'PM'), ('Bunschoten', 'AE'), ('van Soolingen', 'D')])
        
    def test_get_dois(self):
        dois = self.source1.get_dois()
        self.assertEqual(dois, ["10.1111/j.1365-2958.1993.tb00976.x"])
        dois = self.source2.get_dois()
        self.assertEqual(dois, ["10.1111/j.1365-2958.1993.tb00976.x"])
        dois = self.source3.get_dois()
        self.assertEqual(dois, ["10.1073/pnas.112047299"])
        
    def test_get_pmids(self):
        pmids = self.source1.get_pmids()
        self.assertEqual(pmids, ["7934856"])
        pmids = self.source2.get_pmids()
        self.assertEqual(pmids, ["7934856"])
        pmids = self.source3.get_pmids()
        self.assertEqual(pmids, ["12032318"])

    def test_get_pmc(self):
        pmcs = self.source3.get_pmcs()
        self.assertEqual(pmcs, ["124276"])
        
if __name__ == "__main__":
    unittest.main()
