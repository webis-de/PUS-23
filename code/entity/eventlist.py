from .event import Event
from csv import reader
    
class EventList:

    def __init__(self, filepath, bibliography):

        self.events = []

        with open(filepath) as file:
            csv_reader = reader(file, delimiter=",")
            #skip header
            next(csv_reader)
            for row in csv_reader:
                try:
                    args = [row[i].strip() for i in range(12)] + [bibliography]
                    self.events.append(Event(*args))
                except ValueError:
                    print("Could not parse " + str(row))
