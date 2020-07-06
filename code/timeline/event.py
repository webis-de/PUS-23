from pprint import pformat
from timeline.bibentry import Bibentry

class Event:

    def __init__(self, row):
        
        self.date = row[0].strip()
        self.event = row[1].strip()
        self.comment = row[3].strip()
        self.type_of_event = row[4].strip()
        self.location = row[5].strip()
        self.doi1 = row[6].strip()
        self.doi2 = row[7].strip()
        
        self.bibentry1 = Bibentry(row[8])
        self.bibentry2 = Bibentry(row[9])

    def __str__(self):
        return pformat({"date":self.date,
                        "event":self.event,
                        "comment":self.comment,
                        "type_of_event":self.type_of_event,
                        "location":self.location,
                        "doi1":self.doi1,
                        "doi2":self.doi2,
                        "bibentry1":self.bibentry1.__dict__,
                        "bibentry2":self.bibentry2.__dict__}, width=200) + "\n"
