class Bibentry:
    """
    Wrapper class for bibentry.

    Attributes:
        bibkey: The bibkey of this bibentry.
        title: The title of this bibentry.
        authors: The authors of this bibentry.
        doi: The doi of this bibentry.
        pmid: The pmid of this bibentry.
        year: The year of this bibentry.
    """
    def __init__(self, bibentry):

        self.bibkey = bibentry.key
        self.title = self.replace_braces(bibentry.fields.get("title", ""))
        self.authors = [self.replace_braces(person.last_names[0]) for person in bibentry.persons.get("author") if self.replace_braces(person.last_names[0])]
        self.doi = bibentry.fields.get("doi", "")
        self.pmid = bibentry.fields.get("pmid", "")
        self.year = bibentry.fields.get("year", "")

    def replace_braces(self, value):
        if type(value) == str:
            return value.replace("{","").replace("}","")
        elif type(value) == list:
            return [string.replace("{","").replace("}","") for string in value]
        elif type(value) == tuple:
            return tuple(string.replace("{","").replace("}","") for string in value)
        else:
            ""

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.bibkey == other.bibkey

    def __ne__(self, other):
        return not self == other
