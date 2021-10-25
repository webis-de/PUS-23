from csv import reader

class Person:

    def __init__(self, last_names):
        self.last_names = [last_names]

class PybcsvItem:

    def __init__(self, key, title, journal, doi, pmid, year, last_names):

        self.key = key
        self.fields = {"title":title,
                       "journal":journal,
                       "doi":doi,
                       "pmid":pmid,
                       "year":year}
        self.persons = {"author":[Person(last_name)
                                  for last_name in last_names]}

class Pybcsv:

    def __init__(self, filepath):

        self.entries = {}
        with open(filepath) as file:
            csv_reader = reader(file, delimiter = "|")
            for wos_key, title, doi, pmid in csv_reader:
                self.entries[wos_key] = PybcsvItem(wos_key,
                                                   title,
                                                   None,
                                                   doi,
                                                   pmid,
                                                   1000,
                                                   ["None"])
            
def parse_file(filepath):
    return Pybcsv(filepath)
