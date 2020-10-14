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
        self.keywords = [keyword.replace("\"", "") for keyword in split("; *", keywords)]

    def parse_int(self, value):
        try:
            return int(value)
        except ValueError:
            return None

    def __str__(self):
        copy = self.__dict__.copy()
        copy["papers"] = [{"fields":paper.fields._dict,"persons":paper.persons._dict} for paper in self.papers]
        return self.prettyprint(copy)

    def prettyprint(self, structure, indent = ""):
        if structure and type(structure) == dict:
            return "\n".join([indent + str(pair[0]) + "\n" + self.prettyprint(pair[1], indent + "    ") for pair in structure.items()])
        elif structure and type(structure) == list:
            return "\n".join(self.prettyprint(item, indent) for item in structure)
        else:
            if structure:
                return indent + str(structure)
            else:
                return indent + "-"


