from .event import Event
from csv import reader
    
class EventList:

    def __init__(self, filepath, bibliography, accountlist):

        self.events = []

        with open(filepath) as file:
            csv_reader = reader(file, delimiter=",")
            #skip header
            header = next(csv_reader)
            for row in csv_reader:
                try:
                    args = {header[i].strip():row[i].strip() for i in range(len(header))}
                    args["bibliography"] = bibliography
                    args["accountlist"] = accountlist
                    self.events.append(Event(**args))
                except ValueError:
                    print("Could not parse " + str(row))


