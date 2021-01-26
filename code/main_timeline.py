from bibliography.bibliography import Bibliography
from timeline.accountlist import AccountList
from timeline.eventlist import EventList
from pprint import pprint

###############################################################
# This file serves as an entry point view events and accounts.#
###############################################################

def heading(text):
    print(text)
    print("-"*len(text))
    print()

if __name__ == "__main__":

    conditions = []

    EQUALLING = ["bibentries"]

    for equalling in [[], EQUALLING]:

        if equalling:
            print("EQULLING OVER",equalling)
        else:
            print("NOT EQUALLING EVENTS.")

        bibliography = Bibliography("../data/tracing-innovations-lit.bib")
        accountlist = AccountList("../data/CRISPR_accounts.csv")
        eventlist = EventList("../data/CRISPR_publication-events.csv", bibliography, accountlist, conditions, equalling)

        event_types = {}

        for event in eventlist.events:
            event_type = event.type if event.type else "-"
            event_extracted_from = event.extracted_from if event.extracted_from else "-"
            if event_type not in event_types:
                event_types[event_type] = {}
            if event_extracted_from not in event_types[event_type]:
                event_types[event_type][event_extracted_from] = 0
            event_types[event_type][event_extracted_from] += 1

        heading("\nEVENT TYPES")
        pprint(event_types, width=10)

        event_count = 0

        for event in eventlist.events:
            for condition in conditions:
                if not eval(condition):
                    break
            else:
                event_count += 1

        heading("\nEVENT COUNT")
        print(len(eventlist.events), "(all)\n")
        print(event_count, "with conditions:")

        print("".join(["\n - " + condition for condition in conditions]))

        heading("\nEVENTS WITH BIBENTRIES")

        print(len([event for event in eventlist.events if event.bibentries]))

        print("="*100)

        
