from os.path import basename, dirname, sep
from json import load, dumps
from utils import parse_json_name, parse_article_title
from glob import glob
from csv import writer

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

json_paths = sorted(glob("../../analysis/bibliography/2021_11_01/publication-events-highly-cited/*_correct.json"))

relative = True

for json_path in json_paths:
    with open(json_path) as file:
        events = load(file)

    json_name = parse_json_name(json_path)
    article_title = parse_article_title(json_name).replace(" correct", "")

    method_matrix = [[[0,0] for _ in range(len(methods))] for _ in methods]
    strategy_matrix = [[[0,0] for _ in range(len(strategies))] for _ in strategies]

    for event in events:
        for i in range(len(strategies)):
            for j in range(len(strategies)):
                if i == j:
                    strategy_matrix[i][j] = ""
                elif any(event["trace"][article_title]["first_mentioned"][strategies[i]].values()) and \
                     any(event["trace"][article_title]["first_mentioned"][strategies[j]].values()):
                    strategy_matrix[i][j][1] += 1
                    if min([value["index"] for value in event["trace"][article_title]["first_mentioned"][strategies[j]].values() if value]) > min([value["index"] for value in event["trace"][article_title]["first_mentioned"][strategies[i]].values() if value]):
                        strategy_matrix[i][j][0] += 1
        results = {k:v for k,v in list(event["trace"][article_title]["first_mentioned"]["verbatim"].items()) + list(event["trace"][article_title]["first_mentioned"]["relaxed"].items())}

        for i in range(len(methods)):
            for j in range(len(methods)):
                if i == j:
                    method_matrix[i][j] = ""
                elif results[methods[i]] and results[methods[j]]:
                    method_matrix[i][j][1] += 1
                    if results[methods[j]]["index"] > results[methods[i]]["index"]:
                        method_matrix[i][j][0] += 1

    for i in range(len(methods)):
        for j in range(len(methods)):
            if i != j:
                try:
                    method_matrix[i][j] = str(int(method_matrix[i][j][0] * 100 / method_matrix[i][j][1]))  if relative else method_matrix[i][j][0]
                except ZeroDivisonError:
                    method_matrix[i][j] = "0.00"

    for i in range(len(strategies)):
        for j in range(len(strategies)):
            if i != j:
                try:
                    strategy_matrix[i][j] = str(int(strategy_matrix[i][j][0] * 100 / strategy_matrix[i][j][1])) if relative else strategy_matrix[i][j][0]
                except ZeroDivisonError:
                    strategy_matrix[i][j] = "0.00"

    with open(json_path.replace("_correct.json", "_confusion.csv"), "w") as file:
        csv_writer = writer(file, delimiter=",")
        width = 16

        print(" "*width + "".join([method.rjust(width, " ") for method in methods]))
        csv_writer.writerow([""] + [method for method in methods])
        print("\n\n\n")

        for index,line in enumerate(method_matrix):
            print(methods[index].rjust(width, " ") + "".join([str(item).rjust(width, " ") for item in line]))
            csv_writer.writerow([methods[index]] + [str(item) for item in line])
            print("\n\n\n\n\n")
                
        print(" "*width + "".join([strategy.rjust(width, " ") for strategy in strategies]))
        csv_writer.writerow([""] + [strategy for strategy in strategies])
        print("\n\n\n")

        for index,line in enumerate(strategy_matrix):
            print(strategies[index].rjust(width, " ") + "".join([str(item).rjust(width, " ") for item in line]))
            csv_writer.writerow([strategies[index]] + [str(item) for item in line])
            print("\n\n\n")
