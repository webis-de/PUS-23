from os.path import basename, dirname, sep
from json import load, dumps
from path import json_path

excluded_methods = [#"ned <= 0.2",
                    "ned <= 0.3",
                    "ned <= 0.4",
                    "ned_and_ratio",
                    "ned_and_jaccard",
                    #"ned_and_skat"
                    ]

with open(json_path) as file:
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
        
with open(json_path.replace(".json", "_reduced.json"), "w") as file:
    file.write("[" + "\n")
    file.write(",\n".join([dumps(event) for event in reduced_events]))
    file.write("\n" + "]")
