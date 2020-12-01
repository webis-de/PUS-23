from bibliography.bibliography import Bibliography
from timeline.accountlist import AccountList
from timeline.eventlist import EventList
from pprint import pprint

el = EventList("../data/CRISPR_events - events.csv",
               Bibliography("../data/tracing-innovations-lit.bib"),
               AccountList("../data/CRISPR_events - accounts.csv"))

event_types = [event.type for event in el.events]
event_types = {event_type:event_types.count(event_type) for event_type in set(event_types)}

pprint(event_types)

print("="*50)
print(el.events[124])
print("="*50)
pprint(el.events[124].json())
