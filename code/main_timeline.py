from bibliography.bibliography import Bibliography
from timeline.accountlist import AccountList
from timeline.eventlist import EventList
from pprint import pprint
from glob import glob

###############################################################
# This file serves as an entry point view events and accounts.#
###############################################################

if __name__ == "__main__":

    bibliography = Bibliography("../data/CRISPR_literature.csv")
    accountlist = AccountList("../data/CRISPR_accounts.csv")
        
    conditions = []

    EQUALLING = ["bibentries"]

    for eventfilename in glob("../data/CRISPR_publication-events*.csv"):
        print(eventfilename.split("/")[-1] + "\n")
        for equalling in [[], EQUALLING]:

            if equalling:
                print("EQULLING OVER", " AND ".join(equalling))
            else:
                print("NOT EQUALLING EVENTS.")

            eventlist = EventList(eventfilename, bibliography, accountlist, conditions, equalling)

            event_types = {}

            for event in eventlist.events:
                event_type = event.type if event.type else "-"
                event_extracted_from = event.extracted_from if event.extracted_from else "-"
                if event_type not in event_types:
                    event_types[event_type] = {}
                if event_extracted_from not in event_types[event_type]:
                    event_types[event_type][event_extracted_from] = 0
                event_types[event_type][event_extracted_from] += 1

            print("\nEVENT TYPES")
            pprint(event_types, width=10)

            event_count = 0

            for event in eventlist.events:
                for condition in conditions:
                    if not eval(condition):
                        break
                else:
                    event_count += 1

            print(len(eventlist.events), "events,", len([event for event in eventlist.events if event.bibentries]), "events with bibentries")

            if not equalling: print("-"*70)

        print("="*70)

        
