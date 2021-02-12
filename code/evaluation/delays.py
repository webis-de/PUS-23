from json import load
from pprint import pprint
from path import JSON_CORRECT
from datetime import datetime

def median(array):
    array = sorted(array)
    if len(array)%2 == 1:
        return array[int(len(array)/2)] / 1
    else:
        return (array[int(len(array)/2)] + array[int(len(array)/2) -1]) / 2

def mean(array):
    return sum(array)/len(array)

def delta(timestamp1, timestamp2):
    date1 = datetime.strptime(timestamp1, "%Y-%m-%d %H:%M:%S")
    date2 = datetime.strptime(timestamp2, "%Y-%m-%d %H:%M:%S")
    return (date2 - date1).days

method_delays = {"absolute":{},"relative":{}}

data = load(open(JSON_CORRECT))

for event in data:
    
    for strategy in event["first_mentioned"]:
        for method,result in event["first_mentioned"][strategy].items():
            if method not in method_delays["relative"]:
                method_delays["relative"][method] = []
            if method not in method_delays["absolute"]:
                method_delays["absolute"][method] = []
                
    methods_sorted = sorted([item for item in list(event["first_mentioned"]["verbatim"].items()) + list(event["first_mentioned"]["relaxed"].items()) if item[1]], key = lambda item: item[1]["index"])

    if methods_sorted:
        best_method = methods_sorted[0]
        method_delays["relative"][best_method[0]].append(0)
        for method,result in methods_sorted[1:]:
            method_delays["relative"][method].append(delta(best_method[1]["timestamp"], result["timestamp"]))
    
    for strategy in event["first_mentioned"]:
        for method,result in event["first_mentioned"][strategy].items():
            if result:
                delay = int(result["timestamp"][:4]) - max(2005, event["event_year"])
                method_delays["absolute"][method].append(delay)

for key in ["absolute","relative"]:
    print(key, "delay")
    print()
    for method,delays in method_delays[key].items():
        value = sorted(delays)
        print("\t", method)
        print("\t", "mean delay", mean(delays))
        print("\t", "median delay", median(delays))
        print("\t", "="*50)
    print()
