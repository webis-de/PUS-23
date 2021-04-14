from Levenshtein import distance
from unicodedata import normalize

def to_ascii(string):
    return normalize("NFD",string).encode("ASCII","ignore").decode("ASCII")

def to_lower(string):
    return string.lower()

def to_alnum(string):
    return "".join([character for character in string if character.isalnum() or character in [" "]])

def levenshtein(event_title, source_title):
    return distance(to_alnum(to_ascii(to_lower(event_title))), to_alnum(to_ascii(to_lower(source_title))))/len(to_alnum(to_ascii(to_lower(event_title))))

def exact_match(event_authors, source_text):
    return len([event_author for event_author in event_authors if event_author in source_text])/len(event_authors)

def jaccard(list1, list2):
    intersection = set(list1).intersection(set(list2))
    union = set(list1).union(set(list2))
    return len(intersection)/len(union)

def skat(gains, ideal, expected, provided):
    score = 0
    for position, item in enumerate(provided, 1):
        if item in gains:
            if expected.index(item) == provided.index(item):
                score += gains[item]/position
            else:
                score -= gains[item]/position
    return score/ideal

source_title = "CRISPR elements in Yersinia pestis acquire repeats by preferential uptake of bacteriophage DNA, provide additional tools for evolutionary study"
event_title = "CRISPR elements in Yersinia pestis acquire new repeats by preferential uptake of bacteriophage DNA, and provide additional tools for evolutionary studies"
print("source2 ned",levenshtein(event_title, source_title))

print("===========")

source_title = "Efficient genome editing in zebrafish using a CRISPR-Cas system"
event_title = "Efficient genome editing in plants using a CRISPR/Cas system"
print("source3 ned",levenshtein(event_title, source_title))

print("===========")

source_title = "A programmable dual-DNA-guided RNA endonuclease in adaptive bacterial immunity"
event_title = "A programmable dual-RNA-guided DNA endonuclease in adaptive bacterial immunity"
print("source4 ned",levenshtein(event_title, source_title))
event_authors = ["Jinek", "Chylinski", "Fonfara", "Hauer", "Doudna", "Charpentier"]
source_text = 'Chylinski K, Jinek M, Fonfara I, Hauer M, Doudna JA, Charpentier E (August 2012). "AA programmable dual-DNA-guided RNA endonuclease in adaptive bacterial immunity". Science. 337 (6096): 816–821. Bibcode:2012Sci...337..816J. doi:10.1126/science.1225829. PMC 6286148. PMID 22745249.'
gains = {author:len(event_authors) - event_authors.index(author) for author in event_authors}
ideal = sum([(gains.get(event_author, 0))/index for index,event_author in enumerate(event_authors, 1)])
referenced_author_set_ascii = ["Chylinski", "Jinek", "Fonfara", "Hauer", "Doudna", "Charpentier"]
print("source4 exact_match",exact_match(event_authors, source_text))
print("source4 jaccard",jaccard(event_authors, referenced_author_set_ascii))
print("source4 skat",skat(gains, ideal, event_authors, referenced_author_set_ascii))

print("===========")

source_title = "Clustered regularly interspaced short palindromic repeats (CRISPRs) have spacers of extrachromosomal origin"
event_title = "Clustered regularly interspaced short palindrome repeats (CRISPRs) have spacers of extrachromosomal origin"
print("source5 ned",levenshtein(event_title, source_title))
event_authors = ["Bolotin", "Quinquis", "Sorokin", "Ehrlich"]
source_text = 'Doe J, Dae J, Bolotin A, Quinquis B, Sorokin A, Ehrlich SD (August 2005). "Clustered regularly interspaced short palindromic repeats (CRISPRs) have spacers of extrachromosomal origin". Microbiology. 151 (Pt 8): 2551–2561. doi:10.1099/mic.0.28048-0. '
gains = {author:len(event_authors) - event_authors.index(author) for author in event_authors}
ideal = sum([(gains.get(event_author, 0))/index for index,event_author in enumerate(event_authors, 1)])
referenced_author_set_ascii = ["Doe", "Dae", "Bolotin", "Quinquis", "Sorokin", "Ehrlich"]
print("source5 exact_match",exact_match(event_authors, source_text))
print("source5 jaccard",jaccard(event_authors, referenced_author_set_ascii))
print("source5 skat",skat(gains, ideal, event_authors, referenced_author_set_ascii))

print("===========")

source_title = "Multiplex genome engineering use CRISPR/Cas systems"
event_title = "Multiplex genome engineering using CRISPR/Cas systems"
print("source6 ned",levenshtein(event_title, source_title))
event_authors = ["Cong", "Ran", "Cox", "Lin", "Barretto", "Hsu", "Habib", "Wu", "Jiang", "Marraffini", "Zhang"]
source_text = 'Cong L, Ran FA, Cox D, Lin S, Barretto R, Hsu PD, Habib N, Wu X, Jiang W, Marraffini LA, Zhang F (February 2013). "Multiplex genome engineering use CRISPR/Cas systems". Science. 339 (6121): 819–823. Bibcode:2013Sci...339..819C. doi:10.1126/science.1231143. PMC 3795411. PMID 23287718.'
gains = {author:len(event_authors) - event_authors.index(author) for author in event_authors}
ideal = sum([(gains.get(event_author, 0))/index for index,event_author in enumerate(event_authors, 1)])
referenced_author_set_ascii = ["Cong", "Ran", "Cox", "Lin", "Barretto", "Habib", "Hsu", "Wu", "Jiang", "Marraffini", "Zhang"]
print("source6 exact_match",exact_match(event_authors, source_text))
print("source6 jaccard",jaccard(event_authors, referenced_author_set_ascii))
print("source6 skat",skat(gains, ideal, event_authors, referenced_author_set_ascii))
