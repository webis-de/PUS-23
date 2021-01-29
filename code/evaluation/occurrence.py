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

def calculate_and_write_occurrence_table(json_path, sort):

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
                       "any": {"data":
                               [item for item in publication_events if
                                item["first_mentioned"]["verbatim"]["titles"] or
                                item["first_mentioned"]["verbatim"]["dois"] or 
                                item["first_mentioned"]["verbatim"]["pmids"] or
                                item["first_mentioned"]["relaxed"]["ned <= 0.2"] or
                                item["first_mentioned"]["relaxed"]["ned <= 0.3"] or
                                item["first_mentioned"]["relaxed"]["ned <= 0.4"] or
                                item["first_mentioned"]["relaxed"]["ned_and_ratio"] or
                                item["first_mentioned"]["relaxed"]["ned_and_jaccard"] or
                                item["first_mentioned"]["relaxed"]["ned_and_skat"]],
                               "note":"any of the strategies above"},
                       "verbatim": {"data":
                                    [item for item in publication_events if
                                     item["first_mentioned"]["verbatim"]["titles"] or
                                     item["first_mentioned"]["verbatim"]["dois"] or
                                     item["first_mentioned"]["verbatim"]["pmids"]],
                                    "note":"any of the verbatim strategies above"},
                       "verbatim|ned <= 0.2|ned_and_ratio|ned_and_jaccard|ned_and_skat": {"data":
                                                                                              [item for item in publication_events if
                                                                                               item["first_mentioned"]["verbatim"]["titles"] or
                                                                                               item["first_mentioned"]["verbatim"]["dois"] or
                                                                                               item["first_mentioned"]["verbatim"]["pmids"] or
                                                                                               item["first_mentioned"]["relaxed"]["ned <= 0.2"] or
                                                                                               item["first_mentioned"]["relaxed"]["ned_and_ratio"] or
                                                                                               item["first_mentioned"]["relaxed"]["ned_and_jaccard"] or
                                                                                               item["first_mentioned"]["relaxed"]["ned_and_skat"]],
                                                                                              "note":"any of the verbatim strategies or title edit distance less or equal 0.2 or any of the relaxed strategies with authors"},
                       "verbatim|ned_and_ratio|ned_and_jaccard|ned_and_skat": {"data":
                                                                                  [item for item in publication_events if
                                                                                   item["first_mentioned"]["verbatim"]["titles"] or
                                                                                   item["first_mentioned"]["verbatim"]["dois"] or
                                                                                   item["first_mentioned"]["verbatim"]["pmids"] or
                                                                                   item["first_mentioned"]["relaxed"]["ned_and_ratio"] or
                                                                                   item["first_mentioned"]["relaxed"]["ned_and_jaccard"] or
                                                                                   item["first_mentioned"]["relaxed"]["ned_and_skat"]],
                                                                                  "note":"any of the verbatim strategies or any of the relaxed strategies with authors"}
                       }

            file.write("number of events" + "," + str(len(publication_events)) + "\n")
            file.write("\n")
            file.write("Strategy Employed to Identify First Occurrence" + "," + "Absolute" + "," + "Relative" + "," + "Notes" + "\n")
            file.write("--- Verbatim Match Measures ---" + "\n")
            for key,value in results.items():
                if key == "any":
                    file.write("--- Combined Measures ---" + "\n")
                file.write(key + "," + str(len(value["data"])) + "," + str(round(len(value["data"])/len(publication_events)*100, 2)) + "," + value["note"] + "\n")
                if key == "pmids":
                    file.write("--- Relaxed Match Measures ---" + "\n")
            file.write("\n")

def calculate_delays_and_write_table_and_plot(json_file, skip_no_result):

    data = sorted([event for event in load(open(json_file)) if event["bibentries"]], key=lambda event: int(event["event_year"]))

    bibkey_list = [list(event["bibentries"].keys())[0] for event in data]
    event_year_list = [int(event["event_year"]) if event["event_year"] else None for event in data]

    verbatim_title_list = [int(event["first_mentioned"]["verbatim"]["titles"]["timestamp"][:4]) if event["first_mentioned"]["verbatim"]["titles"] else None for event in data]
    verbatim_doi_list = [int(event["first_mentioned"]["verbatim"]["dois"]["timestamp"][:4]) if event["first_mentioned"]["verbatim"]["dois"] else None for event in data]
    verbatim_pmid_list = [int(event["first_mentioned"]["verbatim"]["pmids"]["timestamp"][:4]) if event["first_mentioned"]["verbatim"]["pmids"] else None for event in data]
    ned_02_list = [int(event["first_mentioned"]["relaxed"]["ned <= 0.2"]["timestamp"][:4]) if event["first_mentioned"]["relaxed"]["ned <= 0.2"] else None for event in data]
    ned_03_list = [int(event["first_mentioned"]["relaxed"]["ned <= 0.3"]["timestamp"][:4]) if event["first_mentioned"]["relaxed"]["ned <= 0.3"] else None for event in data]
    ned_04_list = [int(event["first_mentioned"]["relaxed"]["ned <= 0.4"]["timestamp"][:4]) if event["first_mentioned"]["relaxed"]["ned <= 0.4"] else None for event in data]
    ned_and_ratio_list = [int(event["first_mentioned"]["relaxed"]["ned_and_ratio"]["timestamp"][:4]) if event["first_mentioned"]["relaxed"]["ned_and_ratio"] else None for event in data]
    ned_and_jaccard_list = [int(event["first_mentioned"]["relaxed"]["ned_and_jaccard"]["timestamp"][:4]) if event["first_mentioned"]["relaxed"]["ned_and_jaccard"] else None for event in data]
    ned_and_skat_list = [int(event["first_mentioned"]["relaxed"]["ned_and_skat"]["timestamp"][:4]) if event["first_mentioned"]["relaxed"]["ned_and_skat"] else None for event in data]

    original_lists = [bibkey_list, event_year_list, verbatim_title_list, verbatim_doi_list, verbatim_pmid_list, ned_02_list, ned_03_list, ned_04_list, ned_and_ratio_list, ned_and_jaccard_list, ned_and_skat_list]

    if skip_no_result:
        value_lists = original_lists[2:]
        reduced_lists = []

        for original_list in original_lists:
            reduced_list = []
            for i in range(len(original_list)):
                if len([value_list[i] for value_list in value_lists if value_list[i]]) > 0:
                    reduced_list.append(original_list[i])
            reduced_lists.append(reduced_list)

        for i in range(len(original_lists)):
            original_lists[i] = reduced_lists[i]

    bibkey_list = original_lists[0]
    event_year_list = original_lists[1]
    verbatim_title_delays = [calculate_delay(match, year) for match,year in zip(original_lists[2], event_year_list)]
    verbatim_doi_delays = [calculate_delay(match, year) for match,year in zip(original_lists[3], event_year_list)]
    verbatim_pmid_delays = [calculate_delay(match, year) for match,year in zip(original_lists[4], event_year_list)]
    ned_02_delays = [calculate_delay(match, year) for match,year in zip(original_lists[5], event_year_list)]
    ned_03_delays = [calculate_delay(match, year) for match,year in zip(original_lists[6], event_year_list)]
    ned_04_delays = [calculate_delay(match, year) for match,year in zip(original_lists[7], event_year_list)]
    ned_and_ratio_delays = [calculate_delay(match, year) for match,year in zip(original_lists[8], event_year_list)]
    ned_and_jaccard_delays = [calculate_delay(match, year) for match,year in zip(original_lists[9], event_year_list)]
    ned_and_skat_delays = [calculate_delay(match, year) for match,year in zip(original_lists[10], event_year_list)]

    with open(dirname(json_file) + sep + "occurrence" + "_by_bibkey" + ("_all" if not skip_no_result else "") + ".csv", "w") as file:
        file.write("bibkey" + "," + \
                   "event_year" + "," + \
                   "verbatim_title" + "," + \
                   "verbatim_doi" + "," + \
                   "verbatim_pmid" + "," + \
                   "ned <= 0.2" + "," + \
                   "ned <= 0.3" + "," + \
                   "ned <= 0.4" + "," + \
                   "ned_and_ratio" + "," + \
                   "ned_and_jaccard" + "," + \
                   "ned_and_skat" + "\n")

        for bibkey, event_year, verbatim_title_delay, verbatim_doi_delay, verbatim_pmid_delay, ned_02_delay, ned_03_delay, ned_04_delay, ned_and_ratio_delay, ned_and_jaccard_delay, ned_and_skat_delay in \
            zip(bibkey_list, event_year_list, verbatim_title_delays, verbatim_doi_delays, verbatim_pmid_delays, ned_02_delays, ned_03_delays, ned_04_delays, ned_and_ratio_delays, ned_and_jaccard_delays, ned_and_skat_delays):
            file.write(str(bibkey) + "," + \
                       str(event_year) + "," + \
                       stringify_delay(verbatim_title_delay) + "," + \
                       stringify_delay(verbatim_doi_delay) + "," + \
                       stringify_delay(verbatim_pmid_delay) + "," + \
                       stringify_delay(ned_02_delay) + "," + \
                       stringify_delay(ned_03_delay) + "," + \
                       stringify_delay(ned_04_delay) + "," + \
                       stringify_delay(ned_and_ratio_delay) + "," + \
                       stringify_delay(ned_and_jaccard_delay) + "," + \
                       stringify_delay(ned_and_skat_delay) + "\n")

        if not skip_no_result:
            file.write("\n")
            file.write("OCCURRENCE,")
            for i in range(2, len(original_lists)):
                file.write("," + str(round(len([item for item in original_lists[i] if item])/len(original_lists[i])*100, 2)))
            

    if skip_no_result:
        event_year_list = [str(year) for year in original_lists[1]]
        '''
        year = event_year_list[0]
        for i in range(1, len(event_year_list)):
            if event_year_list[i] == year:
                event_year_list[i] = ""
            else:
                year = event_year_list[i]
        '''

        width = 0.08
        x = np.arange(len(bibkey_list))
        plt.figure(figsize=(60, 12.5), dpi=200)
        plt.subplots_adjust(bottom=0.15, top=0.99, left=0.01, right=0.998)
        plt.margins(x=0.0005, y=0.005)
        plt.xticks(np.arange(len(bibkey_list)), bibkey_list, rotation=90)
        plt.xlabel("PUBLICATIONS\n(colours represent different matching strategies as per legend | column hints of 0.1 represent no match or false positive (negative delay) | all matches +0.25 to visualise same-year occurrence)")
        plt.ylabel("OCCURRENCE DELAY IN YEARS")
        plt.bar(x - width*4, verbatim_title_delays, width=width, label="verbatim_title")
        plt.bar(x - width*3, verbatim_doi_delays, width=width, label="verbatim_doi")
        plt.bar(x - width*2, verbatim_pmid_delays, width=width, label="verbatim_pmid")
        plt.bar(x - width*1, ned_02_delays, width=width, label="ned <= 0.2")
        plt.bar(x + width*0, ned_03_delays, width=width, label="ned <= 0.3")
        plt.bar(x + width*1, ned_04_delays, width=width, label="ned <= 0.4")
        plt.bar(x + width*2, ned_and_ratio_delays, width=width, label="ned_and_ratio")
        plt.bar(x + width*3, ned_and_jaccard_delays, width=width, label="ned_and_jaccard")
        plt.bar(x + width*4, ned_and_skat_delays, width=width, label="ned_and_skat")
        plt.legend()
        plt.savefig(dirname(json_file) + sep + "delays.png")

if __name__ == "__main__":

    json_file = "../../analysis/TEST/2021_01_29_18_39_55/CRISPR_de.json"
    
    calculate_and_write_occurrence_table(json_file, False)
    calculate_delays_and_write_table_and_plot(json_file, True)
    calculate_delays_and_write_table_and_plot(json_file, False)


