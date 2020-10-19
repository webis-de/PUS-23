from re import split

class Event:

    def __init__(self, ID, year, month, day, event, typ, subtyp, actors, places, papers, source, keywords, bibliography):

        self.ID = int(ID)
        self.year = self.parse_int(year)
        self.month = self.parse_int(month)
        self.day = self.parse_int(day)
        self.event = event
        self.typ = typ
        self.subtyp = subtyp
        self.actors = [actor.strip() for actor in split(", +", actors.strip()) if actor.strip()]
        self.places = [place.strip() for place in split(", +", places.strip()) if place.strip()]
        self.papers = [bibliography.bibentries.get(paper) for paper in split("; *", papers.strip()) if paper]
        self.dois = [paper.fields.get("doi") for paper in self.papers]
        self.titles = [self.replace_braces(paper.fields.get("title")) for paper in self.papers]
        self.authors = [[self.replace_braces(person.last_names[0]) for person in paper.persons.get("author")] for paper in self.papers]
        self.keywords = [keyword.replace("\"", "") for keyword in split("; *", keywords)]
        self.occurrences = {"all_dois":None,"all_full_titles":None,"80_percent_of_words_in_stopped_titles":None,"all_keywords_in_one_section":None}

    def parse_int(self, value):
        try:
            return int(value)
        except ValueError:
            return None

    def replace_braces(self, value):
        if type(value) == str:
            return value.replace("{","").replace("}","")
        if type(value) == list:
            return [string.replace("{","").replace("}","") for string in value]
        if type(value) == tuple:
            return tuple(string.replace("{","").replace("}","") for string in value)

    def __str__(self):
        copy = self.__dict__.copy()
        copy["papers"] = [{"fields":paper.fields._dict,"persons":paper.persons._dict} for paper in self.papers]
        return self.prettyprint(copy)

    def prettyprint(self, structure, indent = ""):
        if structure and type(structure) == dict:
            return "\n".join([indent + str(pair[0]) + "\n" + self.prettyprint(pair[1], indent + "    ") for pair in structure.items()])
        elif structure and type(structure) == list:
            return indent + "[" + "\n" + ",\n".join([self.prettyprint(item, " " + indent) for item in structure]) + "\n" + indent + "]"
        else:
            if structure:
                return indent + str(structure)
            else:
                return indent + "-"


