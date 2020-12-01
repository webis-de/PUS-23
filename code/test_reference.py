from article.revision.source import Source
from preprocessor.preprocessor import Preprocessor
from utility.logger import Logger
from lxml import html
from os import remove, rename, rmdir
from shutil import rmtree
from os.path import exists, sep
from hashlib import sha256

TEST_DIRECTORY = ".." + sep + "test"
#Reference with title in quotation marks.
SOURCE1 = '<li id="cite_note-Groenen1993-24"><span class="mw-cite-backlink"><b><a href="#cite_ref-Groenen1993_24-0">^</a></b></span> ' + \
         '<span class="reference-text"><cite id="CITEREFGroenenBunschotenvan_Soolingenvan_Embden1993" ' + \
         'class="citation journal cs1">Groenen PM, Bunschoten AE, van Soolingen D, van Emden JD (1993). ' + \
         '"Nature of DNA polymorphism in the direct repeat cluster of Mycobacterium tuberculosis; ' + \
         'application for strain differentiation by a novel typing method". <i>Molecular Microbiology</i> (10): 1057&#8211;65. ' + \
         '<a href="/wiki/Doi_(identifier)" class="mw-redirect" title="Doi (identifier)">doi</a>:' + \
         '<a rel="nofollow" class="external text" href="https://doi.org/10.1111%2Fj.1365-2958.1993.tb00976.x">10.1111/j.1365-2958.1993.tb00976.x</a>. ' + \
         '<a href="/wiki/PMID_(identifier)" class="mw-redirect" title="PMID (identifier)">PMID</a>&#160;' + \
         '<a rel="nofollow" class="external text" href="//pubmed.ncbi.nlm.nih.gov/7934856">7934856</a>.</cite><span'

#Reference with title without quotation marks, PMID spaced and followed by letters, names with 'et al.', first names abbreviated with '.' and separated by ';' instead of ','
SOURCE2 = '<li id="cite_note-Groenen1993-24"><span class="mw-cite-backlink"><b><a href="#cite_ref-Groenen1993_24-0">^</a></b></span> ' + \
         '<span class="reference-text"><cite id="CITEREFGroenenBunschotenvan_Soolingenvan_Embden1993" ' + \
         'class="citation journal cs1">Groenen PM; Bunschoten AE, van Soolingen D. et al. (1993). ' + \
         'Nature of DNA polymorphism in the direct repeat cluster of Mycobacterium tuberculosis; ' + \
         'application for strain differentiation by a novel typing method. <i>Molecular Microbiology</i> (10): 1057&#8211;65. ' + \
         'a wild doi appears 10.1111/j.1365-2958.1993.tb00976.x. ' + \
         '<a href="/wiki/PMID_(identifier)" class="mw-redirect" title="PMID (identifier)">PMID</a>&#160;' + \
         '<a rel="nofollow" class="external text" href="//pubmed.ncbi.nlm.nih.gov/7934856">     7934856FOOBAR</a>.</cite><span'

def test_text(logger):
    logger.start("Testing reference text extraction")
    
    source = Source(html.fromstring(SOURCE1), 24)
    text = source.get_text()
    print(text)
    assert text== 'Groenen PM, Bunschoten AE, van Soolingen D, van Emden JD (1993). ' + \
                  '"Nature of DNA polymorphism in the direct repeat cluster of Mycobacterium tuberculosis; ' + \
                  'application for strain differentiation by a novel typing method". ' + \
                  'Molecular Microbiology (10): 1057–65. doi:10.1111/j.1365-2958.1993.tb00976.x. PMID 7934856.'

    source = Source(html.fromstring(SOURCE2), 24)
    text = source.get_text()
    print(text)
    assert text== 'Groenen PM; Bunschoten AE, van Soolingen D. et al. (1993). ' + \
                  'Nature of DNA polymorphism in the direct repeat cluster of Mycobacterium tuberculosis; ' + \
                  'application for strain differentiation by a novel typing method. ' + \
                  'Molecular Microbiology (10): 1057–65. a wild doi appears 10.1111/j.1365-2958.1993.tb00976.x. PMID      7934856FOOBAR.'
    
    logger.stop("Reference text extraction successful.", 1)

def test_get_title(logger):
    logger.start("Testing reference title extraction")

    for SOURCE in [SOURCE1, SOURCE2]:
        source = Source(html.fromstring(SOURCE), 24)
        title = source.get_title("en")
        assert title == "Nature of DNA polymorphism in the direct repeat cluster of Mycobacterium tuberculosis; " + \
                        "application for strain differentiation by a novel typing method"

    logger.stop("Reference title extraction successful.", 1)

def test_get_authors(logger):
    logger.start("Testing reference authors extraction")
    
    source = Source(html.fromstring(SOURCE1), 24)
    authors = source.get_authors("en")
    print(authors)
    assert authors == [('Groenen', 'PM'), ('Bunschoten', 'AE'), ('van Soolingen', 'D'), ('van Emden', 'JD')]

    source = Source(html.fromstring(SOURCE2), 24)
    authors = source.get_authors("en")
    print(authors)
    assert authors == [('Groenen', 'PM'), ('Bunschoten', 'AE'), ('van Soolingen', 'D')]
    
    logger.stop("Reference authors extraction successful.", 1)

def test_get_dois(logger):
    logger.start("Testing reference dois extraction")

    for SOURCE in [SOURCE1, SOURCE2]:
        source = Source(html.fromstring(SOURCE), 24)
        dois = source.get_dois()
        print(dois)
        assert dois == ["10.1111/j.1365-2958.1993.tb00976.x"]
    
    logger.stop("Reference dois extraction successful.", 1)

def test_get_pmids(logger):
    logger.start("Testing reference pmid extraction")

    for SOURCE in [SOURCE1, SOURCE2]:
        source = Source(html.fromstring(SOURCE), 24)
        pmids = source.get_pmids()
        print(pmids)
        assert pmids == ["7934856"]
    
    logger.stop("Reference pmid extraction successful.", 1)

if __name__ == "__main__":     
    
    with Logger(TEST_DIRECTORY) as LOGGER:
        test_text(LOGGER)
        test_get_title(LOGGER)
        test_get_authors(LOGGER)
        test_get_dois(LOGGER)
        test_get_pmids(LOGGER)
