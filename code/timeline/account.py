class Account:

    def __init__(self, args):

        self.account_id = int(args["account_id"])
        self.reference = args["reference"]
        self.scholar_citation_count = self.int(args["scholar_citation_count"])
        self.url = args["url"]
        self.account_title = args["account_title"]
        self.wos_ut = args["wos_ut"]
        self.type = args["type"]
        self.genre = args["genre"]
        self.dynamic = args["dynamic"]
        self.account_year = self.int(args["account_year"])
        self.account_month = self.int(args["account_month"])
        self.account_day = self.int(args["account_day"])
        self.account_date = self.date(args["account_year"], args["account_month"], args["account_day"])
        self.about = args["about"]
        self.bib_keys = args["bib_keys"]
        self.publisher_author = args["publisher_author"]
        self.comment = args["comment"]
        self.doi = args["doi"]
        self.pmid = args["pmid"]
        self.pmc = args["pmc"]
        self.shortname = args["shortname"]

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
        copy = self.__dict__.copy()
        del copy["account_year"]
        del copy["account_month"]
        del copy["account_day"]
        del copy["publisher_author"]
        del copy["about"]
        return "\t" + "\n\t".join([str(item[0]) + ": " + str(item[1]) for item in copy.items()])
