from os.path import basename, dirname, sep
from json import load, dumps
from path import json_path

methods = ["titles", 
           "dois",
           "pmids",
           "ned <= 0.2",
           "ned <= 0.3",
           "ned <= 0.4",
           "ned_and_ratio",
           "ned_and_jaccard",
           "ned_and_skat"
           ]

strategies = ["verbatim", "relaxed"]

with open(json_path) as file:
    events = load(file)

method_matrix = [[0]*len(methods) for _ in methods]
strategy_matrix = [[0,0],[0,0]]

for event in events:
    if any(event["first_mentioned"]["verbatim"].values()) and not any(event["first_mentioned"]["relaxed"].values()):
        strategy_matrix[0][1] += 1
    if any(event["first_mentioned"]["relaxed"].values()) and not any(event["first_mentioned"]["verbatim"].values()):
        strategy_matrix[1][0] += 1
    results = {k:v for k,v in list(event["first_mentioned"]["verbatim"].items()) + list(event["first_mentioned"]["relaxed"].items())}
    for i in range(len(methods)):
        for j in range(len(methods)):
            if results[methods[i]] and not results[methods[j]]:
                method_matrix[i][j] += 1
width = 16

print(" "*width + "".join([method.rjust(width, " ") for method in methods]))
print()
print()
print()

for index,line in enumerate(method_matrix):
    print(methods[index].rjust(width, " ") + "".join([str(item).rjust(width, " ") for item in line]))
    print()
    print()
    print()

print("="*100)
        
print(" "*width + "".join([strategy.rjust(width, " ") for strategy in strategies]))
print()
print()
print()

for index,line in enumerate(strategy_matrix):
    print(strategies[index].rjust(width, " ") + "".join([str(item).rjust(width, " ") for item in line]))
    print()
    print()
    print()
