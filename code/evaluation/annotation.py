from os.path import basename, dirname, exists, sep
from glob import glob
from json import load, dumps
from utils import parse_json_name, parse_article_title
from csv import reader, writer
from pprint import pprint
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

def get_bibliography_data(event):
    bibkey = list(event["bibentries"].keys())[0]
    title = event["bibentries"][bibkey]["title"]
    authors = event["bibentries"][bibkey]["authors"]
    doi = event["bibentries"][bibkey]["doi"]
    pmid = event["bibentries"][bibkey]["pmid"]
    year = event["bibentries"][bibkey]["year"]
    return (bibkey, title, authors, doi, pmid, year)

def concatenate_bibliography_data(title, authors, doi, pmid, year):
    return ("Title: " + title + "\n" +
            "Authors: " + "[" + ", ".join(authors) + "]" + "\n" +
            "DOI: " + doi + "\n" +
            "PMID: " + pmid + "\n" +
            "Year: " + year)    

directory = "../../analysis/bibliography/2021_11_03_analysed_2"

json_paths = sorted([path for path
                     in glob(directory + "/publication-events-highly-cited/*.json")
                     if not any([path.endswith(suffix) for suffix in ["_correct.json", "_annotated.json", "_reduced.json"]])])

to_label_filepath = directory + "/to_label.csv"
labelled_filepath = directory + "/labelled.csv"

reference_match_mapping = {}

overview_precisions = {method:[] for method in verbatim_methods + relaxed_methods}

for json_path in json_paths:

    with open(json_path) as file:
        events = load(file)
    json_name = parse_json_name(json_path)
    article_title = parse_article_title(json_name)

    print(article_title + ":", json_path)

    if not exists(to_label_filepath):
            
        for index, event in enumerate(events):
            bibkey, title, authors, doi, pmid, year = get_bibliography_data(event)
            concatenated_bibliography_data = concatenate_bibliography_data(title, authors, doi, pmid, year)
            for strategy in event["trace"][article_title]["first_mentioned"]:
                for method,result in event["trace"][article_title]["first_mentioned"][strategy].items():
                    if result:
                        if method in ["dois","pmids"]:
                            continue
                        elif method == "titles":
                            if (event["trace"][article_title]["first_mentioned"]["verbatim"]["dois"] and
                                (event["trace"][article_title]["first_mentioned"]["verbatim"]["dois"]["index"] ==
                                 event["trace"][article_title]["first_mentioned"]["verbatim"]["titles"]["index"]) or
                                event["trace"][article_title]["first_mentioned"]["verbatim"]["pmids"] and
                                (event["trace"][article_title]["first_mentioned"]["verbatim"]["pmids"]["index"] ==
                                 event["trace"][article_title]["first_mentioned"]["verbatim"]["titles"]["index"])):
                                continue
                            else:
                                go_to_link = result["result"][bibkey]
                                if concatenated_bibliography_data not in reference_match_mapping:
                                    reference_match_mapping[concatenated_bibliography_data] = {}
                                reference_match_mapping[concatenated_bibliography_data][go_to_link] = ""
                        else:
                            raw_reference = result["result"][bibkey]["source_text"]["raw"]
                            if not any([(doi and doi in raw_reference),
                                        (pmid and pmid in raw_reference)]):
                                if concatenated_bibliography_data not in reference_match_mapping:
                                    reference_match_mapping[concatenated_bibliography_data] = {}
                                reference_match_mapping[concatenated_bibliography_data][raw_reference] = ""
    else:
        if exists(labelled_filepath):

            reference_match_mapping = {}
            with open(labelled_filepath, encoding="utf-8") as labeled_file:
                csv_reader = reader(labeled_file, delimiter=",")
                for concatenated_bibliography_data,match,judgement1,judgement2 in csv_reader:
                    if concatenated_bibliography_data not in reference_match_mapping:
                        reference_match_mapping[concatenated_bibliography_data] = {}
                    reference_match_mapping[concatenated_bibliography_data][match] = (judgement1 == "y")
            
            precisions = {method:[0,0] for method in verbatim_methods + relaxed_methods}

            with open(json_path) as file:
                events = load(file)

            for index, event in enumerate(events):
                bibkey, title, authors, doi, pmid, year = get_bibliography_data(event)
                concatenated_bibliography_data = concatenate_bibliography_data(title, authors, doi, pmid, year)
                for strategy in event["trace"][article_title]["first_mentioned"]:
                    for method,result in event["trace"][article_title]["first_mentioned"][strategy].items():
                        if result:
                            #add method to result
                            events[index]["trace"][article_title]["first_mentioned"][strategy][method]["method"] = method
                            if method in ["dois","pmids"]:
                                correct = True
                            elif method == "titles":
                                if (event["trace"][article_title]["first_mentioned"]["verbatim"]["dois"] and
                                    (event["trace"][article_title]["first_mentioned"]["verbatim"]["dois"]["index"] ==
                                     event["trace"][article_title]["first_mentioned"]["verbatim"]["titles"]["index"]) or
                                    event["trace"][article_title]["first_mentioned"]["verbatim"]["pmids"] and
                                    (event["trace"][article_title]["first_mentioned"]["verbatim"]["pmids"]["index"] ==
                                     event["trace"][article_title]["first_mentioned"]["verbatim"]["titles"]["index"])):
                                    correct = True
                                else:
                                    go_to_link = result["result"][bibkey]
                                    correct = reference_match_mapping[concatenated_bibliography_data][go_to_link] 
                            else:
                                raw_reference = result["result"][bibkey]["source_text"]["raw"]
                                if any([(doi and doi in raw_reference),
                                        (pmid and pmid in raw_reference)]):
                                    correct = True
                                else:
                                    correct = reference_match_mapping[concatenated_bibliography_data][raw_reference]
                            if correct:
                                precisions[method][0] += 1
                            precisions[method][1] += 1
                            events[index]["trace"][article_title]["first_mentioned"][strategy][method]["correct"] = correct

            first_event = True
            first_correct_event = True
            first_reduced_event = True
                    
            with open(json_path.replace(".json", "_annotated.json"), "w") as annotated_file,\
                 open(json_path.replace(".json", "_correct.json"), "w") as correct_file,\
                 open(json_path.replace(".json", "_reduced.json"), "w") as reduced_file:
                annotated_file.write("[")
                correct_file.write("[")
                reduced_file.write("[")

                for event in events:

                    annotated_file.write("," * (not first_event) + "\n")
                    first_event = False
                    
                    annotated_file.write(dumps(event))
                    
                    for strategy in event["trace"][article_title]["first_mentioned"]:
                        for method in event["trace"][article_title]["first_mentioned"][strategy]:
                            if event["trace"][article_title]["first_mentioned"][strategy][method] and not event["trace"][article_title]["first_mentioned"][strategy][method]["correct"]:
                                event["trace"][article_title]["first_mentioned"][strategy][method] = None

                    methods_with_results = [item for item in event["trace"][article_title]["first_mentioned"]["verbatim"].values() if item] + \
                                           [item for item in event["trace"][article_title]["first_mentioned"]["relaxed"].values() if item]
                    
                    if any(methods_with_results):

                        correct_file.write("," * (not first_correct_event) + "\n")
                        first_correct_event = False
                        
                        correct_file.write(dumps(event))

                        correct_methods = [item for item in methods_with_results if item["correct"]]
                        
                        if any(correct_methods):
                            earliest_result = sorted(correct_methods, key = lambda item: item["index"])[0]
                            event["trace"][article_title]["first_mentioned"] = earliest_result

                            reduced_file.write("," * (not first_reduced_event) + "\n")
                            first_reduced_event = False
                                
                            reduced_file.write(dumps(event))

                annotated_file.write("\n" + "]")
                correct_file.write("\n" + "]")
                reduced_file.write("\n" + "]")

            with open(json_path.replace(".json", "_precision.csv"), "w") as precision_file:
                precision_csv_writer = writer(precision_file, delimiter=",")
                for method, score in precisions.items():
                    precision = str(round(score[0]/score[1], 4)) if score[1] > 0 else "na"
                    if score[1] > 0:
                        overview_precisions[method].append(score[0]/score[1])
                    precision_csv_writer.writerow([method, str(score[0]), str(score[1]), precision])

pprint(overview_precisions)

with open(dirname(json_path) + sep + "0_precision.csv", "w") as precision_overview_file:
    precision_overview_csv_writer = writer(precision_overview_file, delimiter=",")
    for method, values in overview_precisions.items():
        precision_overview_csv_writer.writerow([method,
                                                round(numpy.mean(values),4),
                                                round(numpy.median(values),4),
                                                round(numpy.std(values),4)])

if not exists(to_label_filepath):
    with open(to_label_filepath, "w") as to_label_file:
        to_label_csv_writer = writer(to_label_file, delimiter=",")
        for concatenated_bibliography_data,matches in reference_match_mapping.items():
            for match in matches:
                to_label_csv_writer.writerow([concatenated_bibliography_data, match, ""])
