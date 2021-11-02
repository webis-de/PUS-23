from .event import Event
from csv import reader
from json import dumps
    
class EventList:
    """
    Wrapper class to collect events.

    Attributes:
        events: A list of Event objects.
    """
    def __init__(self, filepath, bibliography, accountlist, conditions = [], equalling = []):
        """
        Initialises the EventList.

        Providing Bibentry attributes in 'equalling' will base Events' equals function on those fields.

        Args:
            filepath: The path to the event CSV.
            bibliography: A Bibliography object.
            accountlist: A AccountList object.
            conditions: Conditions according to which events will be selected.
            equalling: Bibentry attributes as strings to which Events will be reduced.
        """
        self.events = []
        #eventset to ensure duplicate-free eventlist but preserve event order
        eventset = set()

        with open(filepath) as file:
            csv_reader = reader(file, delimiter=",")
            header = next(csv_reader)
            for row_number, row in enumerate(csv_reader, 1):
                try:
                    args = {header[i].strip():row[i].strip() for i in range(len(header))}
                    #create event object from arguments and bibliography
                    event = Event(args, bibliography, accountlist, equalling)
                    #check conditions and skip events not matching them
                    for condition in conditions:
                        if not eval(condition):
                            break
                    else:
                        #check if event is already present in list of events; uses equalling attribues
                        if event not in eventset:
                            #check equalling attributes and skip events who have no values for those attributes
                            for attribute in equalling:
                                if not eval("event." + attribute):
                                    break
                            else:
                                eventset.add(event)
                                self.events.append(event)
                except ValueError:
                    print("Could not parse row " + str(row_number) + " in events: " + str(row))

    def write_text(self, output_filepath):
        """
        Writes events to file in string format.

        Args:
            output_filepath: The path to the output file.
        """
        with open(output_filepath, "w") as file:
            file.write(("\n"+"-"*50+"\n").join([str(event) for event in self.events]))

    def write_json(self, output_filepath):
        """
        Writes events to file in JSON format.

        Args:
            output_filepath: The path to the output file.
        """
        with open(output_filepath, "w") as file:
            file.write("[\n")
            file.write(",\n".join([dumps(event.json()) for event in self.events]))
            file.write("\n]")

