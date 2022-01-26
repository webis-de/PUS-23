from json import load
from datetime import datetime
from glob import glob
from utils import parse_json_name, parse_article_title
from csv import writer
import numpy

verbatim_methods = ["titles",
                    "dois",
                    "pmids"]

relaxed_methods = ["ned <= 0.2",
                   "ned <= 0.3",
                   "ned <= 0.4",
                   "ned_and_ratio",
                   "ned_and_jaccard",
                   "ned_and_skat"
                   ]

def median(array):
    if len(array) == 0:
        return "n/a"
    return int(numpy.median(array))

def mean(array):
    if len(array) > 0:
        return round(numpy.mean(array), 1)
    else:
        return "n/a"

def std(array):
    return round(numpy.std(array), 1)

def delta(timestamp1, timestamp2):
    date1 = datetime.strptime(timestamp1, "%Y-%m-%d %H:%M:%S")
    date2 = datetime.strptime(timestamp2, "%Y-%m-%d %H:%M:%S")
    return (date2 - date1).days

json_paths = sorted(glob("../../../analysis/bibliography/2021_11_03_evaluated_2/publication-events-field-matched/*_correct.json"))

for json_path in json_paths:
    method_delays = {"absolute":{},"relative":{}}

    data = load(open(json_path))
    json_name = parse_json_name(json_path)
    article_title = parse_article_title(json_name).replace(" correct", "")

    for event in data:
        
        for strategy in event["trace"][article_title]["first_mentioned"]:
            for method,result in event["trace"][article_title]["first_mentioned"][strategy].items():
                if method not in method_delays["relative"]:
                    method_delays["relative"][method] = []
                if method not in method_delays["absolute"]:
                    method_delays["absolute"][method] = []
                    
        methods_sorted = sorted([item for item in list(event["trace"][article_title]["first_mentioned"]["verbatim"].items()) + list(event["trace"][article_title]["first_mentioned"]["relaxed"].items()) if item[1]], key = lambda item: item[1]["index"])

        if methods_sorted:
            best_method = methods_sorted[0]
            method_delays["relative"][best_method[0]].append(0)
            for method,result in methods_sorted[1:]:
                method_delays["relative"][method].append(delta(best_method[1]["timestamp"], result["timestamp"]))
        
        for strategy in event["trace"][article_title]["first_mentioned"]:
            for method,result in event["trace"][article_title]["first_mentioned"][strategy].items():
                if result:
                    delay = int(result["timestamp"][:4]) - max(2005, event["event_year"])
                    method_delays["absolute"][method].append(delay)

    with open(json_path.replace("_correct.json","_delays.csv"), "w") as file:
        csv_writer = writer(file, delimiter=",")
        csv_writer.writerow(["","absolute delay","","relative delay",""])
        csv_writer.writerow(["","mean","median","mean","median"])
        for method in verbatim_methods + relaxed_methods:
            csv_writer.writerow([method,
                                 mean(method_delays["absolute"][method]),
                                 median(method_delays["absolute"][method]),
                                 mean(method_delays["relative"][method]),
                                 median(method_delays["relative"][method])])
