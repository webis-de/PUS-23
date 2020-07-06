from re import findall
from pprint import pformat

class Bibentry:

    def __init__(self, entry):

        self.entry = entry.strip().replace("\n"," ")
        
        try:
            self.title = findall(r"\(\d\d\d\d\)\. [^\.]*\.", self.entry)[0][7:-1].strip().lower()
        except:
            self.title = ""

        try:
            self.authors = findall(r"^[\w,\. \-&´áéíóú]*\. ", self.entry)[0].strip().lower()
        except:
            self.authors = ""

    def __str__(self):
        return pformat({"entry":self.entry, "title":self.title, "authors":self.authors})

if __name__ == "__main__":

    bibentry = Bibentry("Hullahalli, K., Rodrigues, M., Schmidt, B., Li, X., Bhardwaj, P., & Palmer, K. (2015). Comparative Analysis of the Orphan CRISPR2 Locus in 242 Enterococcus faecalis Strains. 10(9), E0138890")
    print(bibentry)
