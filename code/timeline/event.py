from re import split, sub
from copy import deepcopy

class Event:

    def __init__(self, args, bibliography, accountlist, equalling = []):

        self.event_id = int(args["event_id"])
        self.event_year = self.int(args["event_year"])
        self.event_month = self.int(args["event_month"])
        self.event_day = self.int(args["event_day"])
        self.event_date = self.date(args["event_year"], args["event_month"], args["event_day"])
        self.account = accountlist.accounts[int(args["account_id"])]
        self.sampled = bool(args["sampled"])
        self.event_text = args["event_text"]
        self.type = args["type"]
        self.subtype = args["subtype"]
        #self.actors = [actor.strip() for actor in split("[,;] *", args["actors"].strip()) if actor.strip()]
        #self.places = [place.strip() for place in split("[,;] *", args["places"].strip()) if place.strip()]
        #self.keywords = [keyword.replace("\"", "").strip() for keyword in split("; *", args["keywords"]) if keyword.strip()]
        self.bibentries = bibliography.get_bibentries(split("; *", args["bib_keys"]))
        self.wos_keys = args["wos_keys"]
        self.extracted_from = args["extracted_from"]
        self.comment = args["comment"]
        self.titles = {bibentry.bibkey:bibentry.title for bibentry in self.bibentries}
        self.authors = {bibentry.bibkey:bibentry.authors for bibentry in self.bibentries}
        self.dois = [bibentry.doi for bibentry in self.bibentries]
        self.pmids = [bibentry.pmid for bibentry in self.bibentries]
        self.equalling = equalling
        self.first_mentioned = {}

    def int(self, value):
        try:
            return int(value)
        except ValueError:
            return None

    def date(self, year, month, day):
        account_date = ""
        if year:
            account_date += str(year)
        else:
            account_date += "YYYY"
        if month:
            account_date += "-" + str(month).rjust(2, "0")
        else:
            account_date += "-" + "MM"
        if day:
            account_date += "-" + str(day).rjust(2, "0")
        else:
            account_date += "-" + "DD"
        return account_date

    def __str__(self):
        copy = self.json()
        if copy["account"]:
            copy["account"] = {"account_date":self.account.account_date,"account_url":self.account.url, "account_id":self.account.account_id}
        else:
            copy["account"] = None
        del copy["event_year"]
        del copy["event_month"]
        del copy["event_day"]
        del copy["comment"]
        del copy["sampled"]
        del copy["extracted_from"]
        del copy["equalling"]
        return self.prettyprint(copy)

    def json(self):
        copy = deepcopy(self.__dict__)
        try:
            copy["account"] = self.account.__dict__
        except AttributeError:
            copy["account"] = None
        copy["bibentries"] = {bibentry.bibkey:bibentry.__dict__ for bibentry in copy["bibentries"]}
        return copy

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

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        if self.equalling:
            for value in self.equalling:
                if not eval("self." + value) == eval("other." + value):
                    break
            else:
                return True
        else:
            if self.event_id == other.event_id:
                return True
        return False

    def __ne__(self, other):
        return not self == other
