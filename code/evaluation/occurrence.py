import matplotlib.pyplot as plt
from json import load
from os.path import basename, dirname, sep
from glob import glob
import numpy as np
from utils import parse_json_name, parse_article_title
from csv import writer

#constants
NO_MATCH_OR_NEGATIVE = 0.05
ZERO = 0.25
ARTICLE_YEAR = 2005

def calculate_delay(match_year, event_year):
    if match_year != None:
        delay = match_year - max(event_year, ARTICLE_YEAR)
        if delay < 0:
            return NO_MATCH_OR_NEGATIVE
        else:
            return delay + ZERO
    else:
        return NO_MATCH_OR_NEGATIVE

def stringify_delay(delay):
    if delay == NO_MATCH_OR_NEGATIVE:
        return "-"
    else:
        return str(int(delay - ZERO))

def occurrence(json_path, sort, rows):

    directory = dirname(json_path)
    json_name = parse_json_name(json_path)
    article_title = parse_article_title(json_name)

    with open(json_path) as file:
        data = [event for event in load(file) if event["bibentries"]]

    account_ids = sorted(set([event["account"]["account_id"] for event in data]), key = lambda x: int(x))

    if sort:
        publication_events_by_account = {account_id:[] for account_id in account_ids}

        for publication_event in data:
            publication_events_by_account[publication_event["account"]["account_id"]].append(publication_event)
    else:
        publication_events_by_account = {"ALL ACOUNT IDs":[] for account_id in account_ids}

        for publication_event in data:
            publication_events_by_account["ALL ACOUNT IDs"].append(publication_event)   

    with open(directory + sep + json_name + "_" + "occurrence" + ("_by_account" if sort else "") + ".csv", "w") as file:
        for account_id, publication_events in publication_events_by_account.items():

            file.write("Account ID: " + str(account_id) + "\n")
            file.write("\n")
            results = {"titles": {"data": [item for item in publication_events if item["trace"][article_title]["first_mentioned"]["verbatim"]["titles"]],
                                  "note": "each title occurs verbatim in revision"},
                       "dois": {"data": [item for item in publication_events if item["trace"][article_title]["first_mentioned"]["verbatim"]["dois"]],
                                "note":"each doi occurs verbatim in revision"},
                       "pmids": {"data": [item for item in publication_events if item["trace"][article_title]["first_mentioned"]["verbatim"]["pmids"]],
                                 "note":"each pmid occurs verbatim in a source (element in References or Further Reading)"},
                       "ned <= 0.2": {"data": [item for item in publication_events if item["trace"][article_title]["first_mentioned"]["relaxed"]["ned <= 0.2"]],
                                      "note":"for each title there is a source with a title with normalised edit distance <= 0.2"},
                       "ned <= 0.3": {"data": [item for item in publication_events if item["trace"][article_title]["first_mentioned"]["relaxed"]["ned <= 0.3"]],
                                      "note":"for each title there is a source with a title with normalised edit distance <= 0.3"},
                       "ned <= 0.4": {"data": [item for item in publication_events if item["trace"][article_title]["first_mentioned"]["relaxed"]["ned <= 0.4"]],
                                      "note":"for each title there is a source with a title with normalised edit distance <= 0.4"},
                       "ned_and_ratio": {"data": [item for item in publication_events if item["trace"][article_title]["first_mentioned"]["relaxed"]["ned_and_ratio"]],
                                     "note":"for each title there is a source with a title with normalised edit distance <= 0.4 and a list of authors with ratio >= 1.0"},
                       "ned_and_jaccard": {"data": [item for item in publication_events if item["trace"][article_title]["first_mentioned"]["relaxed"]["ned_and_jaccard"]],
                                           "note":"for each title there is a source with a title with normalised edit distance <= 0.4 and a list of authors with Jaccard Index >= 0.8"},
                       "ned_and_skat": {"data": [item for item in publication_events if item["trace"][article_title]["first_mentioned"]["relaxed"]["ned_and_skat"]],
                                        "note":"for each title there is a source with a title with normalised edit distance <= 0.4 and a list of authors with Skat >= 0.8"},
                       "any verbatim": {"data": [item for item in publication_events if any([item["trace"][article_title]["first_mentioned"]["verbatim"][key] for key in ["titles","dois","pmids"]])],
                                        "note":"any of the verbatim strategies above"},
                       "verbatim|ned <= 0.2": {"data": [item for item in publication_events if any([item["trace"][article_title]["first_mentioned"]["verbatim"][key] for key in ["titles","dois","pmids"]]) or item["trace"][article_title]["first_mentioned"]["relaxed"]["ned <= 0.2"]],
                                               "note":"any of the verbatim strategies or title edit distance less or equal 0.2"},
                       "verbatim|ned <= 0.3": {"data": [item for item in publication_events if any([item["trace"][article_title]["first_mentioned"]["verbatim"][key] for key in ["titles","dois","pmids"]]) or item["trace"][article_title]["first_mentioned"]["relaxed"]["ned <= 0.3"]],
                                               "note":"any of the verbatim strategies or title edit distance less or equal 0.3"},
                       "verbatim|ned <= 0.4": {"data": [item for item in publication_events if any([item["trace"][article_title]["first_mentioned"]["verbatim"][key] for key in ["titles","dois","pmids"]]) or item["trace"][article_title]["first_mentioned"]["relaxed"]["ned <= 0.4"]],
                                               "note":"any of the verbatim strategies or title edit distance less or equal 0.4"},
                       "verbatim|ned_and_ratio": {"data": [item for item in publication_events if any([item["trace"][article_title]["first_mentioned"]["verbatim"][key] for key in ["titles","dois","pmids"]]) or item["trace"][article_title]["first_mentioned"]["relaxed"]["ned_and_ratio"]],
                                                  "note":"any of the verbatim strategies or title edit distance less or equal 0.4 and a list of authors with ratio >= 1.0"},
                       "verbatim|ned_and_jaccard": {"data": [item for item in publication_events if any([item["trace"][article_title]["first_mentioned"]["verbatim"][key] for key in ["titles","dois","pmids"]]) or item["trace"][article_title]["first_mentioned"]["relaxed"]["ned_and_jaccard"]],
                                                    "note":"any of the verbatim strategies or title edit distance less or equal 0.4 and a list of authors with Jaccard Index >= 0.8"},
                       "verbatim|ned_and_skat": {"data": [item for item in publication_events if any([item["trace"][article_title]["first_mentioned"]["verbatim"][key] for key in ["titles","dois","pmids"]]) or item["trace"][article_title]["first_mentioned"]["relaxed"]["ned_and_skat"]],
                                                 "note":"any of the verbatim strategies or title edit distance less or equal 0.4 and a list of authors with Skat >= 0.8"},
                       "verbatim|ned <= 0.2|ned_and_jaccard|ned_and_skat": {"data":  [item for item in publication_events if
                                                                                      any([item["trace"][article_title]["first_mentioned"]["verbatim"][key] for key in ["titles","dois","pmids"]]) or
                                                                                      any([item["trace"][article_title]["first_mentioned"]["relaxed"][key] for key in ["ned <= 0.2","ned_and_jaccard","ned_and_skat"]])
                                                                                      ],
                                                                            "note":"any of the verbatim strategies or title edit distance less or equal 0.2 or title edit distance less or equal 0.4 and a list of authors with Skat >= 0.8 or Jaccard Index >= 0.8"},
                       "verbatim|ned <= 0.2|ned_and_skat": {"data":[item for item in publication_events if
                                                                    any([item["trace"][article_title]["first_mentioned"]["verbatim"][key] for key in ["titles","dois","pmids"]]) or
                                                                    any([item["trace"][article_title]["first_mentioned"]["relaxed"][key] for key in ["ned <= 0.2","ned_and_skat"]])
                                                                    ],
                                                            "note":"any of the verbatim strategies or title edit distance less or equal 0.2 or title edit distance less or equal 0.4 and a list of authors with Skat >= 0.8"}
                       }

            if rows == {}:
                rows = {key:[] for key in results.keys()}

            file_string = ""
            
            file_string += "number of events" + "," + str(len(publication_events)) + "\n"
            file_string += "\n"
            file_string += "Strategy Employed to Identify First Occurrence" + "," + "Absolute" + "," + "Relative" + "," + "Notes" + "\n"
            file_string += "--- Verbatim Match Measures ---" + "\n"
            for key,value in results.items():
                if key == "any verbatim":
                    file_string += "--- Combined Measures ---" + "\n"
                file_string += key + "," + str(len(value["data"])) + "," + str(round(len(value["data"])/len(publication_events)*100, 2)) + "," + value["note"] + "\n"
                if key == "pmids":
                    file_string += "--- Relaxed Match Measures ---" + "\n"
                rows[key] += [len(value["data"]),
                              round(len(value["data"])/len(publication_events)*100, 2)]
            file_string += "\n"
            file.write(file_string)

            print(article_title + "\n" + ("="*len(article_title)))
            file_string_data = [item.split(",") for item in file_string.split("\n")]
            for line in file_string_data:
                print("".join([item.ljust(len(file_string_data[2][line.index(item)]) + 2, " ") for item in line]))
                
    return rows#article_title + "\n\n" + file_string

def calculate_delays(json_path, skip_no_result):

    article_title = parse_article_title(parse_json_name(json_path))

    #select events with bibentries and (if skip_no_result) with matches, sort by event_year
    data = sorted([event for event in load(open(json_path)) if event["bibentries"] and (any(list(event["trace"][article_title]["first_mentioned"]["verbatim"].values()) + list(event["trace"][article_title]["first_mentioned"]["relaxed"].values())) if skip_no_result else True)],
                  key=lambda event: int(event["event_year"]))

    for event in data:
        for strategy in ["verbatim", "relaxed"]:
            for method in event["trace"][article_title]["first_mentioned"][strategy]:
                if event["trace"][article_title]["first_mentioned"][strategy][method]:
                    event["trace"][article_title]["first_mentioned"][method] = calculate_delay(int(event["trace"][article_title]["first_mentioned"][strategy][method]["timestamp"][:4]),int(event["event_year"]))
                else:
                    event["trace"][article_title]["first_mentioned"][method] = calculate_delay(None,int(event["event_year"]))
            del event["trace"][article_title]["first_mentioned"][strategy]

    return data

def write_delay_table(json_path, data, skip_no_result):

    directory = dirname(json_path)
    json_name = parse_json_name(json_path)
    article_title = parse_article_title(json_name)

    header = ["bibkey","event_year","verbatim_title","verbatim_doi","verbatim_pmid","ned <= 0.2","ned <= 0.3","ned <= 0.4","ned_and_ratio","ned_and_jaccard","ned_and_skat"]

    with open(directory + sep + json_name + "_" + "occurrence" + "_by_bibkey" + ("_all" if not skip_no_result else "") + ".csv", "w") as file:
        file.write(",".join(header) + "\n")

        for event in data:
            file.write(list(event["bibentries"].keys())[0] + "," + \
                       str(event["event_year"]) + "," + \
                       stringify_delay(event["trace"][article_title]["first_mentioned"]["titles"]) + "," + \
                       stringify_delay(event["trace"][article_title]["first_mentioned"]["dois"]) + "," + \
                       stringify_delay(event["trace"][article_title]["first_mentioned"]["pmids"]) + "," + \
                       stringify_delay(event["trace"][article_title]["first_mentioned"]["ned <= 0.2"]) + "," + \
                       stringify_delay(event["trace"][article_title]["first_mentioned"]["ned <= 0.3"]) + "," + \
                       stringify_delay(event["trace"][article_title]["first_mentioned"]["ned <= 0.4"]) + "," + \
                       stringify_delay(event["trace"][article_title]["first_mentioned"]["ned_and_ratio"]) + "," + \
                       stringify_delay(event["trace"][article_title]["first_mentioned"]["ned_and_jaccard"]) + "," + \
                       stringify_delay(event["trace"][article_title]["first_mentioned"]["ned_and_skat"]) + "\n")

def plot_delays(json_path, data, methods):

    directory = dirname(json_path)
    json_name = parse_json_name(json_path)
    article_title = parse_article_title(json_name)
    
    data_map = {method:[] for method in methods}

    for event in data:
        for method in methods:
            data_map[method].append(event["trace"][article_title]["first_mentioned"][method])

    width = 0.8 / len(methods)
    x = np.arange(len(data))
    plt.figure(figsize=(60, 12.5), dpi=200)
    plt.subplots_adjust(bottom=0.15, top=0.99, left=0.01, right=0.998)
    plt.margins(x=0.0005, y=0.005)
    plt.xticks(np.arange(len(data)), [list(event["bibentries"].keys())[0] for event in data], rotation=90)
    plt.xlabel("PUBLICATIONS\n(colours represent different matching strategies as per legend | column hints of 0.05 represent no match or false positive (negative delay) | all matches +0.25 to visualise same-year occurrence)")
    plt.ylabel("OCCURRENCE DELAY IN YEARS")
    i = - int(len(methods) / 2)
    for method,delays in data_map.items():
        plt.bar(x + width*i, delays, width=width, label=method)
        i += 1
    plt.legend()
    plt.savefig(directory + sep + json_name + "_" + "delays.png")

if __name__ == "__main__":

    json_paths = sorted([path for path
                         in glob("../../analysis/bibliography/2021_11_03_analysed_2/publication-events-field/*.json")
                         if not any([path.endswith(suffix) for suffix in ["_correct.json", "_annotated.json", "_reduced.json"]])])

    rows = {}
    for json_path in json_paths:
        rows = occurrence(json_path, False, rows)
        
    with open(dirname(json_paths[0]) + sep + "0_occurrence.csv", "w") as overlook_csv:
        
        article_titles = []
        for json_path in json_paths:
            json_name = parse_json_name(json_path)
            article_titles.append(parse_article_title(json_name))
            article_titles.append("")

        csv_writer = writer(overlook_csv, delimiter=",")
        csv_writer.writerow(["Strategy Employed to Identify First Occurrence"] + \
                            article_titles)
        csv_writer.writerow([""] + ["Absolute","Relative"] * len(json_paths))
        for key, values in rows.items():
            csv_writer.writerow([key] + values)

##            delays = calculate_delays(json_path, True)
##            delays_all = calculate_delays(json_path, False)

##            write_delay_table(json_path, delays, True)
##            write_delay_table(json_path, delays_all, False)

##            methods = ["titles","dois","pmids"]
##            plot_delays(json_path, delays, methods)
