import matplotlib.pyplot as plt
from json import load
from os.path import dirname, sep
import numpy as np

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

def occurrence(json_path, sort):

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

    with open(dirname(json_path) + sep + "occurrence" + ("_by_account" if sort else "") + ".csv", "w") as file:
        for account_id, publication_events in publication_events_by_account.items():

            file.write("Account ID: " + str(account_id) + "\n")
            file.write("\n")
            results = {"titles": {"data": [item for item in publication_events if item["first_mentioned"]["verbatim"]["titles"]],
                                  "note": "each title occurs verbatim in revision"},
                       "dois": {"data": [item for item in publication_events if item["first_mentioned"]["verbatim"]["dois"]],
                                "note":"each doi occurs verbatim in revision"},
                       "pmids": {"data": [item for item in publication_events if item["first_mentioned"]["verbatim"]["pmids"]],
                                 "note":"each pmid occurs verbatim in a source (element in References or Further Reading)"},
                       "ned <= 0.2": {"data": [item for item in publication_events if item["first_mentioned"]["relaxed"]["ned <= 0.2"]],
                                      "note":"for each title there is a source with a title with normalised edit distance <= 0.2"},
                       "ned <= 0.3": {"data": [item for item in publication_events if item["first_mentioned"]["relaxed"]["ned <= 0.3"]],
                                      "note":"for each title there is a source with a title with normalised edit distance <= 0.3"},
                       "ned <= 0.4": {"data": [item for item in publication_events if item["first_mentioned"]["relaxed"]["ned <= 0.4"]],
                                      "note":"for each title there is a source with a title with normalised edit distance <= 0.4"},
                       "ned_and_ratio": {"data": [item for item in publication_events if item["first_mentioned"]["relaxed"]["ned_and_ratio"]],
                                     "note":"for each title there is a source with a title with normalised edit distance <= 0.4 and a list of authors with ratio >= 1.0"},
                       "ned_and_jaccard": {"data": [item for item in publication_events if item["first_mentioned"]["relaxed"]["ned_and_jaccard"]],
                                           "note":"for each title there is a source with a title with normalised edit distance <= 0.4 and a list of authors with Jaccard Index >= 0.8"},
                       "ned_and_skat": {"data": [item for item in publication_events if item["first_mentioned"]["relaxed"]["ned_and_skat"]],
                                        "note":"for each title there is a source with a title with normalised edit distance <= 0.4 and a list of authors with Skat >= 0.8"},
                       "any verbatim": {"data": [item for item in publication_events if any([item["first_mentioned"]["verbatim"][key] for key in ["titles","dois","pmids"]])],
                                        "note":"any of the verbatim strategies above"},
                       "verbatim|ned <= 0.2": {"data": [item for item in publication_events if any([item["first_mentioned"]["verbatim"][key] for key in ["titles","dois","pmids"]]) or item["first_mentioned"]["relaxed"]["ned <= 0.2"]],
                                               "note":"any of the verbatim strategies or title edit distance less or equal 0.2"},
                       "verbatim|ned <= 0.3": {"data": [item for item in publication_events if any([item["first_mentioned"]["verbatim"][key] for key in ["titles","dois","pmids"]]) or item["first_mentioned"]["relaxed"]["ned <= 0.3"]],
                                               "note":"any of the verbatim strategies or title edit distance less or equal 0.3"},
                       "verbatim|ned <= 0.4": {"data": [item for item in publication_events if any([item["first_mentioned"]["verbatim"][key] for key in ["titles","dois","pmids"]]) or item["first_mentioned"]["relaxed"]["ned <= 0.4"]],
                                               "note":"any of the verbatim strategies or title edit distance less or equal 0.4"},
                       "verbatim|ned_and_ratio": {"data": [item for item in publication_events if any([item["first_mentioned"]["verbatim"][key] for key in ["titles","dois","pmids"]]) or item["first_mentioned"]["relaxed"]["ned_and_ratio"]],
                                                  "note":"any of the verbatim strategies or title edit distance less or equal 0.4 and a list of authors with ratio >= 1.0"},
                       "verbatim|ned_and_jaccard": {"data": [item for item in publication_events if any([item["first_mentioned"]["verbatim"][key] for key in ["titles","dois","pmids"]]) or item["first_mentioned"]["relaxed"]["ned_and_jaccard"]],
                                                    "note":"any of the verbatim strategies or title edit distance less or equal 0.4 and a list of authors with Jaccard Index >= 0.8"},
                       "verbatim|ned_and_skat": {"data": [item for item in publication_events if any([item["first_mentioned"]["verbatim"][key] for key in ["titles","dois","pmids"]]) or item["first_mentioned"]["relaxed"]["ned_and_skat"]],
                                                 "note":"any of the verbatim strategies or title edit distance less or equal 0.4 and a list of authors with Skat >= 0.8"},
                       "verbatim|ned <= 0.2|ned_and_jaccard|ned_and_skat": {"data":  [item for item in publication_events if
                                                                                      any([item["first_mentioned"]["verbatim"][key] for key in ["titles","dois","pmids"]]) or
                                                                                      any([item["first_mentioned"]["relaxed"][key] for key in ["ned <= 0.2","ned_and_jaccard","ned_and_skat"]])
                                                                                      ],
                                                                            "note":"any of the verbatim strategies or title edit distance less or equal 0.2 or title edit distance less or equal 0.4 and a list of authors with Skat >= 0.8 or Jaccard Index >= 0.8"},
                       "verbatim|ned <= 0.2|ned_and_skat": {"data":[item for item in publication_events if
                                                                    any([item["first_mentioned"]["verbatim"][key] for key in ["titles","dois","pmids"]]) or
                                                                    any([item["first_mentioned"]["relaxed"][key] for key in ["ned <= 0.2","ned_and_skat"]])
                                                                    ],
                                                            "note":"any of the verbatim strategies or title edit distance less or equal 0.2 or title edit distance less or equal 0.4 and a list of authors with Skat >= 0.8"}
                       }

            file.write("number of events" + "," + str(len(publication_events)) + "\n")
            file.write("\n")
            file.write("Strategy Employed to Identify First Occurrence" + "," + "Absolute" + "," + "Relative" + "," + "Notes" + "\n")
            file.write("--- Verbatim Match Measures ---" + "\n")
            for key,value in results.items():
                if key == "any verbatim":
                    file.write("--- Combined Measures ---" + "\n")
                file.write(key + "," + str(len(value["data"])) + "," + str(round(len(value["data"])/len(publication_events)*100, 2)) + "," + value["note"] + "\n")
                if key == "pmids":
                    file.write("--- Relaxed Match Measures ---" + "\n")
            file.write("\n")

def calculate_delays(json_file, skip_no_result):

    #select events with bibentries and (if skip_no_result) with matches, sort by event_year
    data = sorted([event for event in load(open(json_file)) if event["bibentries"] and (any(list(event["first_mentioned"]["verbatim"].values()) + list(event["first_mentioned"]["relaxed"].values())) if skip_no_result else True)],
                  key=lambda event: int(event["event_year"]))

    for event in data:
        for strategy in ["verbatim", "relaxed"]:
            for method in event["first_mentioned"][strategy]:
                if event["first_mentioned"][strategy][method]:
                    event["first_mentioned"][method] = calculate_delay(int(event["first_mentioned"][strategy][method]["timestamp"][:4]),int(event["event_year"]))
                else:
                    event["first_mentioned"][method] = calculate_delay(None,int(event["event_year"]))
            del event["first_mentioned"][strategy]

    return data

def write_delay_table(json_file, data, skip_no_result):

    header = ["bibkey","event_year","verbatim_title","verbatim_doi","verbatim_pmid","ned <= 0.2","ned <= 0.3","ned <= 0.4","ned_and_ratio","ned_and_jaccard","ned_and_skat"]

    with open(dirname(json_file) + sep + "occurrence" + "_by_bibkey" + ("_all" if not skip_no_result else "") + ".csv", "w") as file:
        file.write(",".join(header) + "\n")

        for event in data:
            file.write(list(event["bibentries"].keys())[0] + "," + \
                       str(event["event_year"]) + "," + \
                       stringify_delay(event["first_mentioned"]["titles"]) + "," + \
                       stringify_delay(event["first_mentioned"]["dois"]) + "," + \
                       stringify_delay(event["first_mentioned"]["pmids"]) + "," + \
                       stringify_delay(event["first_mentioned"]["ned <= 0.2"]) + "," + \
                       stringify_delay(event["first_mentioned"]["ned <= 0.3"]) + "," + \
                       stringify_delay(event["first_mentioned"]["ned <= 0.4"]) + "," + \
                       stringify_delay(event["first_mentioned"]["ned_and_ratio"]) + "," + \
                       stringify_delay(event["first_mentioned"]["ned_and_jaccard"]) + "," + \
                       stringify_delay(event["first_mentioned"]["ned_and_skat"]) + "\n")

def plot_delays(json_file, data, methods):

    data_map = {method:[] for method in methods}

    for event in data:
        for method in methods:
            data_map[method].append(event["first_mentioned"][method])

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
    plt.savefig(dirname(json_file) + sep + "delays.png")

if __name__ == "__main__":

    from path import json_path

    occurrence(json_path, False)

    delays = calculate_delays(json_path, True)
    delays_all = calculate_delays(json_path, False)

    write_delay_table(json_path, delays, True)
    write_delay_table(json_path, delays_all, False)

    methods = ["titles","dois","pmids"]
    plot_delays(json_path, delays, methods)
