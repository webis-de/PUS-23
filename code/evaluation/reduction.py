from os.path import basename, dirname, sep
from json import load, dumps

json_file = "../../analysis/TEST/2021_01_29_18_39_55/CRISPR_de.json"
excluded_methods = ["ned_and_ratio"]

with open(json_file) as file:
    events = load(file)

reduced_events = []

for event in events:
    first_mentioned = event["first_mentioned"]
    occurrences = []
    for verbatim_or_relaxed in first_mentioned:
        for method,occurrence in first_mentioned[verbatim_or_relaxed].items():
            if method not in excluded_methods:
                if occurrence:
                    occurrence["method"] = method
                    occurrences.append(occurrence)
    if occurrences:
        occurrences = sorted(occurrences, key = lambda occurrence: occurrence["index"])
        event["first_mentioned"] = occurrences[0]
        reduced_events.append(event)
        
with open(json_file.replace(".json", "_reduced.json"), "w") as file:
    file.write("[" + "\n")
    file.write(",\n".join([dumps(event) for event in reduced_events]))
    file.write("\n" + "]")
