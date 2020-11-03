from re import split
from copy import deepcopy
from itertools import combinations

class Event:

    def __init__(self, event_id, event_year, event_month, event_day, account_id, sampled, event_text, type, subtype, actors, places, bib_keys, keywords, extracted_from, comment, bibliography, accountlist):

        self.event_id = int(event_id)
        self.event_year = self.parse_int(event_year)
        self.event_month = self.parse_int(event_month)
        self.event_day = self.parse_int(event_day)
        self.event_date = self.get_event_date()
        self.account = accountlist.get_account(account_id)
        self.sampled = bool(sampled.strip())
        self.event_text = event_text
        self.type = type
        self.subtype = subtype
        self.actors = [actor.strip() for actor in split("[,;] *", actors.strip()) if actor.strip()]
        self.places = [place.strip() for place in split("[,;] *", places.strip()) if place.strip()]
        self.bib_keys = [bibliography.bibentries.get(paper) for paper in split("; *", bib_keys.strip()) if bibliography.bibentries.get(paper)]
        self.comment = comment
        self.authors = {paper.fields.get("doi"):[self.replace_braces(person.last_names[0]) for person in paper.persons.get("author")] for paper in self.bib_keys if paper.fields.get("doi")}
        self.dois = [paper.fields.get("doi") for paper in self.bib_keys if paper.fields.get("doi")]
        self.titles = [self.replace_braces(paper.fields.get("title")) for paper in self.bib_keys if self.replace_braces(paper.fields.get("title"))]
        self.keywords = [keyword.replace("\"", "").strip() for keyword in split("; *", keywords) if keyword.strip()]
        self.extracted_from = extracted_from
        self.first_occurrence = {"authors":{doi:{author:None for author in self.authors[doi]} for doi in self.dois},
                                 "dois":{doi:None for doi in self.dois},
                                 "all_dois":None,
                                 "titles":{title:{"full":None, "processed":None} for title in self.titles},
                                 "all_titles":{"full":None, "processed":None},
                                 "keywords":{keyword:None for keyword in self.keywords},
                                 "all_keywords":None,
                                 "actors":{actor:None for actor in self.actors},
                                 "all_actors":None,
                                 "places":{place:None for place in self.places},
                                 "all_places":None}

    def parse_int(self, value):
        try:
            return int(value)
        except ValueError:
            return None

    def get_event_date(self):
        event_date = ""
        if self.event_year:
            event_date += str(self.event_year)
        if self.event_month:
            event_date += "-" + str(self.event_month).rjust(2, "0")
        if self.event_day:
            event_date += "-" + str(self.event_day).rjust(2, "0")
        return event_date

    def replace_braces(self, value):
        if type(value) == str:
            return value.replace("{","").replace("}","")
        if type(value) == list:
            return [string.replace("{","").replace("}","") for string in value]
        if type(value) == tuple:
            return tuple(string.replace("{","").replace("}","") for string in value)

    def __str__(self):
        copy = self.json() #deepcopy(self.__dict__)
        copy["account"] = {"account_date":self.account.account_date,"account_url":self.account.url}
        #copy["bib_keys"] = {paper.key:{"fields":paper.fields._dict.copy(),"persons":paper.persons._dict.copy()} for paper in copy["bib_keys"]}
        del copy["event_year"]
        del copy["event_month"]
        del copy["event_day"]
        del copy["comment"]
        del copy["sampled"]
        del copy["authors"]
        del copy["dois"]
        del copy["titles"]
        del copy["keywords"]
        del copy["extracted_from"]
        return self.prettyprint(copy)

    def json(self):
        copy = deepcopy(self.__dict__)
        copy["account"] = self.account.__dict__
        copy["bib_keys"] = {paper.key:{"fields":paper.fields._dict,"persons":paper.persons._dict} for paper in copy["bib_keys"]}
        for bib_key in copy["bib_keys"]:
            copy["bib_keys"][bib_key]["fields"]["title"] = self.replace_braces(copy["bib_keys"][bib_key]["fields"]["title"])
            for role in copy["bib_keys"][bib_key]["persons"]:
                copy["bib_keys"][bib_key]["persons"][role] = [self.format_person(person) for person in copy["bib_keys"][bib_key]["persons"][role]]
        return copy

    def format_person(self, person):
        return self.replace_braces(person.last_names[0]) + ", " + self.replace_braces(person.first_names[0])

    def prettyprint(self, structure, indent = ""):
        if structure and type(structure) == dict:
            return "\n".join([indent + str(pair[0]) + (":\n" + self.prettyprint(pair[1], indent + "    ") if type(pair[1]) in [dict, list] else ": " + self.prettyprint(pair[1], "")) for pair in structure.items()])
        elif structure and type(structure) == list:
            return indent + "[\n" + ",\n".join([self.prettyprint(item, indent + "    ") for item in structure]) + "\n" + indent + "]"
        else:
            if structure:
                return indent + str(structure)
            else:
                return indent + "-"

    def powerset(self, items, min_len):
        """
        Calculate the powerset of given list.

        Args:
            items: The list for which the powerset should be calculated.
        Returns:
            The powerset.
        """
        return [list(x) for length in range(len(items)+1, min_len-1, -1) for x in combinations(items, length)]
