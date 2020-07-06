from csv import reader
from timeline.event import Event

class Timeline:

    def __init__(self, filename, start, end):

        with open(filename, newline='') as file:
            self.rows = []
            csv_reader = reader(file, delimiter=',')
            line_number = 0
            for row in csv_reader:
                self.rows.append(row)

        self.events = []
        for row in self.rows[start:end]:
            self.events.append(Event(row))

    def print_events(self):
        for event in self.events:
            print(event)

    def get_titles(self):
        titles = []
        for event in self.events:
            if event.title1:
                titles.append(event.title1)
            if event.title2:
                titles.append(event.title2)
        return sorted(list(set(titles)))

    def get_authors(self):
        authors = []
        for event in self.events:
            if event.author1:
                authors.append(event.author1)
            if event.author2:
                authors.append(event.author2)
        return sorted(list(set(authors)))

if __name__ == "__main__":

    timeline = Timeline("../../data/Timeline_Crispr_Cas.csv", 11, 100)
    timeline.print_events()
