from os.path import basename, dirname, sep
from json import load, dumps
from utils import parse_json_name, parse_article_title
from glob import glob
from csv import writer
from pprint import pprint
from numpy import std, mean
from datetime import datetime

def delta(timestamp1, timestamp2):
    date1 = datetime.strptime(timestamp1, "%Y-%m-%d %H:%M:%S")
    date2 = datetime.strptime(timestamp2, "%Y-%m-%d %H:%M:%S")
    return - (date2 - date1).days

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

json_paths = sorted(glob("../../analysis/bibliography/2021_11_03_analysed_2/publication-events-field-matched/*_correct.json"))

relative = True

method_matrices = []
strategy_matrices = []

# [EARLIER_COUNT, EARLIER_RATE, DELTAS, DELTA_MEAN]
SEPARATOR = "/"

for json_path in json_paths:
    print(json_path)
    with open(json_path) as file:
        events = load(file)

    json_name = parse_json_name(json_path)
    article_title = parse_article_title(json_name).replace(" correct", "")

    method_matrix = [[SEPARATOR if i == j else [[],0,[],0] for i in range(len(methods))] for j in range(len(methods))]
    strategy_matrix = [[SEPARATOR if i == j else [[],0,[],0] for i in range(len(strategies))] for j in range(len(strategies))]

    for event in events:
        for i in range(len(strategies)):
            for j in range(len(strategies)):
                if i != j and \
                   any(event["trace"][article_title]["first_mentioned"][strategies[i]].values()) and \
                   any(event["trace"][article_title]["first_mentioned"][strategies[j]].values()):
                    min_i = min([value for value in
                                 event["trace"][article_title]["first_mentioned"][strategies[i]].values()
                                 if value],
                                 key=lambda value:value["index"])
                    min_j = min([value for value in
                                 event["trace"][article_title]["first_mentioned"][strategies[j]].values()
                                 if value],
                                 key=lambda value:value["index"])
                    strategy_matrix[i][j][0].append(int(min_i["index"] < min_j["index"]))
                    strategy_matrix[i][j][2].append(delta(min_i["timestamp"], min_j["timestamp"]))
                    
        results = {k:v for k,v in list(event["trace"][article_title]["first_mentioned"]["verbatim"].items()) + list(event["trace"][article_title]["first_mentioned"]["relaxed"].items())}

        for i in range(len(methods)):
            for j in range(len(methods)):
                if i != j and results[methods[i]] and results[methods[j]]:
                    method_matrix[i][j][0].append(int(results[methods[i]]["index"] < results[methods[j]]["index"]))
                    method_matrix[i][j][2].append(delta(results[methods[i]]["timestamp"], results[methods[j]]["timestamp"]))

    for i in range(len(methods)):
        for j in range(len(methods)):
            if i != j:
                if method_matrix[i][j][0]:
                    method_matrix[i][j][1] = mean(method_matrix[i][j][0])
                else:
                    method_matrix[i][j][1] = "na"
                if method_matrix[i][j][2]:
                    method_matrix[i][j][3] = mean(method_matrix[i][j][2])
                else:
                    method_matrix[i][j][3] = "na"

    for i in range(len(strategies)):
        for j in range(len(strategies)):
            if i != j:
                if strategy_matrix[i][j][0]:
                    strategy_matrix[i][j][1] = mean(strategy_matrix[i][j][0])
                else:
                    strategy_matrix[i][j][1] = "na"
                if strategy_matrix[i][j][2]:
                    strategy_matrix[i][j][3] = mean(strategy_matrix[i][j][2])
                else:
                    strategy_matrix[i][j][3] = "na"

##    if json_path not in ["../../analysis/bibliography/2021_11_03_analysed/publication-events-field/Genome-wide_CRISPR-Cas9_knockout_screens_correct.json",
##                         "../../analysis/bibliography/2021_11_03_analysed/publication-events-field/Restriction_enzyme_correct.json",
##                         "../../analysis/bibliography/2021_11_03_analysed/publication-events-field/CRISPR%2FCas_Tools_correct.json"]:
    if True:
        method_matrices.append(method_matrix)
        strategy_matrices.append(strategy_matrix)

    with open(json_path.replace("_correct.json", "_confusion.csv"), "w") as file:
        csv_writer = writer(file, delimiter=",")
        width = 16

        print(" "*width + "".join([method.rjust(width, " ") for method in methods]))
        csv_writer.writerow([""] + [method + SEPARATOR for method in methods])
        print("\n\n\n")

        for index,line in enumerate(method_matrix):
            earlier_rates = [str(float(round(item[1]*100,1)))
                             if (item != SEPARATOR and item[1] != "na")
                             else (item[1] if item != SEPARATOR else "")
                             for item in line]
            delta_means = [str(float(round(item[3],1))) + " (" + str(float(round(std(item[2]),1))) + ")"
                           if (item != SEPARATOR and item[3] != "na")
                           else (item[1] if item != SEPARATOR else "")
                           for item in line]
            print(methods[index].rjust(width, " ") + \
                  "".join([(item1 + SEPARATOR + item2).rjust(width, " ") for item1,item2 in zip(earlier_rates,delta_means)]))
            csv_writer.writerow([methods[index]] + [item1 + SEPARATOR + item2 for item1,item2 in zip(earlier_rates,delta_means)])
            print("\n\n\n\n\n")
                
        print(" "*width + "".join([strategy.rjust(width, " ") for strategy in strategies]))
        csv_writer.writerow([""] + [strategy + SEPARATOR for strategy in strategies])
        print("\n\n\n")

        for index,line in enumerate(strategy_matrix):
            
            earlier_rates = [str(float(round(item[1]*100,1)))
                             if (item != SEPARATOR and item[1] != "na")
                             else (item[1] if item != SEPARATOR else "")
                             for item in line]
            delta_means = [str(float(round(item[3],1))) + " (" + str(float(round(std(item[2]),1))) + ")"
                           if (item != SEPARATOR and item[3] != "na")
                           else (item[1] if item != SEPARATOR else "")
                           for item in line]
            print(strategies[index].rjust(width, " ") + \
                  "".join([(item1 + SEPARATOR + item2).rjust(width, " ") for item1,item2 in zip(earlier_rates,delta_means)]))
            csv_writer.writerow([strategies[index]] + [item1 + SEPARATOR + item2 for item1,item2 in zip(earlier_rates,delta_means)])
            print("\n\n\n")

method_matrix = [[SEPARATOR if i == j else "" for i in range(len(methods))] for j in range(len(methods))]
strategy_matrix = [[SEPARATOR if i == j else "" for i in range(len(strategies))] for j in range(len(strategies))]

for i in range(len(methods)):
    for j in range(len(methods)):
        if i != j:
            earlier_rates = [matrix[i][j][1] for matrix in method_matrices if matrix[i][j][1] != "na"]
            delta_means = [matrix[i][j][3] for matrix in method_matrices if matrix[i][j][3] != "na"]
            if earlier_rates:
                method_matrix[i][j] += str(float(round(mean(earlier_rates)*100,1))) + " (" + str(float(round(std(earlier_rates)*100,1))) + ")" + SEPARATOR
            else:
                method_matrix[i][j] += "na"  + SEPARATOR
            if delta_means:
                method_matrix[i][j] += str(float(round(mean(delta_means),1))) + " (" + str(float(round(std(delta_means),1))) + ")"
            else:
                method_matrix[i][j] += "na"

for i in range(len(strategies)):
    for j in range(len(strategies)):
        if i != j:
            earlier_rates = [matrix[i][j][1] for matrix in strategy_matrices if matrix[i][j][1] != "na"]
            deltas = []
            for matrix in strategy_matrices:
                deltas += matrix[i][j][2]
            if earlier_rates:
                strategy_matrix[i][j] += str(float(round(mean(earlier_rates)*100,1))) + " (" + str(float(round(std(earlier_rates)*100,1))) + ")" + SEPARATOR
            else:
                strategy_matrix[i][j] += "na"  + SEPARATOR
            if delta_means:
                strategy_matrix[i][j] += str(float(round(mean(deltas),1))) + " (" + str(float(round(std(deltas),1))) + ")"
            else:
                strategy_matrix[i][j] += "na"

with open(dirname(json_paths[0]) + sep + "0_confusion.csv", "w") as file:
    csv_writer = writer(file, delimiter=",")
    csv_writer.writerow([""] + [method + SEPARATOR for method in methods])
    for index,line in enumerate(method_matrix):
        csv_writer.writerow([methods[index]] + line)
    csv_writer.writerow([""])
    csv_writer.writerow([""] + [strategy + SEPARATOR for strategy in strategies])
    for index,line in enumerate(strategy_matrix):
        csv_writer.writerow([strategies[index]] + line)
