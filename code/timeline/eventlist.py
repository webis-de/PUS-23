from .event import Event
from csv import reader
    
class EventList:

    def __init__(self, filepath, bibliography, accountlist, equalling = []):

        self.events = []

        with open(filepath) as file:
            csv_reader = reader(file, delimiter=",")
            #skip header
            header = next(csv_reader)
            row_number = 1
            for row in csv_reader:
                row_number += 1
                try:
                    args = {header[i].strip():row[i].strip() for i in range(len(header))}
                    self.events.append(Event(args, bibliography, accountlist, equalling))
                except ValueError:
                    print("Could not parse row " + str(row_number) + " in events: " + str(row))


