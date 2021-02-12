from os.path import basename, dirname, sep
from json import load, dumps
from path import JSON_CORRECT

methods = ["verbatim",
           "ned <= 0.2",
           "ned <= 0.3",
           "ned <= 0.4",
           "ned_and_ratio",
           "ned_and_jaccard",
           "ned_and_skat"
           ]

strategies = ["verbatim", "relaxed"]

with open(JSON_CORRECT) as file:
    events = load(file)

method_matrix = [[0]*len(methods) for _ in methods]
strategy_matrix = [[0]*len(strategies) for _ in strategies]

for event in events:
    for i in range(len(strategies)):
        for j in range(len(strategies)):
            if any(event["first_mentioned"][strategies[i]].values()) and \
               any(event["first_mentioned"][strategies[j]].values()) and \
               min([value["index"] for value in event["first_mentioned"][strategies[j]].values() if value]) < min([value["index"] for value in event["first_mentioned"][strategies[i]].values() if value]):
                strategy_matrix[i][j] += 1
    #results = {k:v for k,v in list(event["first_mentioned"]["verbatim"].items()) + list(event["first_mentioned"]["relaxed"].items())}
    results = {k:v for k,v in list(event["first_mentioned"]["relaxed"].items())}
    verbatim_methods = [item for item in event["first_mentioned"]["verbatim"].items() if item[1]]
    if verbatim_methods:
        best_verbatim = sorted(verbatim_methods, key = lambda item: item[1]["index"])[0]
        results["verbatim"] = best_verbatim[1]
    else:
        results["verbatim"] = None
    for i in range(len(methods)):
        for j in range(len(methods)):
            if results[methods[i]] and results[methods[j]] and results[methods[j]]["index"] < results[methods[i]]["index"]:
                method_matrix[i][j] += 1
width = 16

print(" "*width + "".join([method.rjust(width, " ") for method in methods]))
print("\n\n\n")

for index,line in enumerate(method_matrix):
    print(methods[index].rjust(width, " ") + "".join([str(item).rjust(width, " ") for item in line]))
    print("\n\n\n")
    print()
    print()
        
print(" "*width + "".join([strategy.rjust(width, " ") for strategy in strategies]))
print("\n\n\n")

for index,line in enumerate(strategy_matrix):
    print(strategies[index].rjust(width, " ") + "".join([str(item).rjust(width, " ") for item in line]))
    print("\n\n\n")
