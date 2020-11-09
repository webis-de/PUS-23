from re import split, sub
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
        #self.actors = [actor.strip() for actor in split("[,;] *", actors.strip()) if actor.strip()]
        #self.places = [place.strip() for place in split("[,;] *", places.strip()) if place.strip()]
        self.bib_keys = [bibliography.bibentries.get(paper) for paper in split("; *", bib_keys.strip()) if bibliography.bibentries.get(paper)]
        self.comment = comment
        self.titles = [self.replace_braces(paper.fields.get("title")) for paper in self.bib_keys if self.replace_braces(paper.fields.get("title"))]
        self.authors = {paper.key:[self.replace_braces(person.last_names[0]) for person in paper.persons.get("author")] for paper in self.bib_keys}
        self.dois = [paper.fields.get("doi") for paper in self.bib_keys if paper.fields.get("doi")]
        self.pmids = [paper.fields.get("pmid") for paper in self.bib_keys if paper.fields.get("pmid")]
        self.keywords = [keyword.replace("\"", "").strip() for keyword in split("; *", keywords) if keyword.strip()]
        self.extracted_from = extracted_from
        self.first_occurrence = {"titles":{"full":{}, "processed":{}},
                                 "authors":{"text":{}, "jaccard":{}, "ndcg":{}},
                                 "dois":{},
                                 "pmids":{},
                                 "keywords":{}
                                 }

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
        elif type(value) == list:
            return [string.replace("{","").replace("}","") for string in value]
        elif type(value) == tuple:
            return tuple(string.replace("{","").replace("}","") for string in value)
        else:
            ""

    def __str__(self):
        copy = self.json()
        copy["account"] = {"account_date":self.account.account_date,"account_url":self.account.url}
        del copy["event_year"]
        del copy["event_month"]
        del copy["event_day"]
        del copy["comment"]
        del copy["sampled"]
        del copy["extracted_from"]
        for bib_key in copy["bib_keys"]:
            copy["bib_keys"][bib_key]["fields"]["title"] = self.replace_braces(copy["bib_keys"][bib_key]["fields"]["title"])
            for role in copy["bib_keys"][bib_key]["persons"]:
                copy["bib_keys"][bib_key]["persons"][role] = [self.format_person(person) for person in copy["bib_keys"][bib_key]["persons"][role]]
##        del copy["authors"]
##        del copy["dois"]
##        del copy["pmids"]
##        del copy["titles"]
##        del copy["keywords"]
        return self.prettyprint(copy)

    def json(self):
        copy = deepcopy(self.__dict__)
        copy["account"] = self.account.__dict__
        copy["bib_keys"] = {paper.key:{"fields":paper.fields._dict,"persons":paper.persons._dict} for paper in copy["bib_keys"]}
        for bib_key in copy["bib_keys"]:
            copy["bib_keys"][bib_key]["fields"]["title"] = self.replace_braces(copy["bib_keys"][bib_key]["fields"]["title"])
            for role in copy["bib_keys"][bib_key]["persons"]:
                copy["bib_keys"][bib_key]["persons"][role] = [person.__dict__ for person in copy["bib_keys"][bib_key]["persons"][role]]
        return copy

    def format_person(self, person):
        return self.replace_braces(person["last_names"][0]) + ", " + self.replace_braces(person["first_names"][0])

    def prettyprint(self, structure, indent = ""):
        if structure and type(structure) == dict:
            return "\n".join([indent + self.linebreak(item[0], indent) +
                              ((":\n" + self.prettyprint(self.linebreak(item[1], indent), indent + "    "))
                              if (type(item[1]) in [dict, list] or (type(item[1]) == str and len(item[1]) > 80))
                              else (": " + self.prettyprint(self.linebreak(item[1], indent), "")))
                              for item in structure.items()])
        elif structure and type(structure) == list:
            return indent + "[\n" + ",\n".join([self.prettyprint(self.linebreak(item, indent), indent + "    ") for item in structure]) + "\n" + indent + "]"
        else:
            if structure not in ["", [], {}, None]:
                return indent + self.linebreak(structure, indent)
            else:
                return indent + "-"

    def linebreak(self, structure, indent):
        if type(structure) not in [dict, list]:
            if type(structure) == str and len(structure) > 80:
                structure = sub(" +", " ", structure.replace("\n", ""))
                return ("\n" + indent).join([str(structure)[i:i+80] for i in range(0,len(str(structure)),80)])
            else:
                return sub(" +", " ", str(structure).replace("\n", ""))
        else:
            return structure
