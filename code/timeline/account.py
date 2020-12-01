class Account:

    def __init__(self, args):

        self.account_id = args["account_id"]
        self.reference = args["reference"]
        self.scholar_cits = args["scholar_cits"]
        self.url = args["url"]
        self.account_title = args["account_title"]
        self.type = args["type"]
        self.genre = args["genre"]
        self.dynamic = args["dynamic"]
        self.account_year = args["account_year"]
        self.account_month = args["account_month"]
        self.account_day = args["account_day"]
        self.account_date = self.get_account_date()
        self.about = args["about"]
        self.bib_keys = args["bib_keys"]
        self.publisher_author = args["publisher_author"]
        self.comment = args["comment"]

    def get_account_date(self):
        account_date = ""
        if self.account_year:
            account_date += str(self.account_year)
        if self.account_month:
            account_date += "-" + str(self.account_month).rjust(2, "0")
        if self.account_day:
            account_date += "-" + str(self.account_day).rjust(2, "0")
        return account_date

    def __str__(self):
        copy = self.__dict__.copy()
        del copy["account_year"]
        del copy["account_month"]
        del copy["account_day"]
        del copy["publisher_author"]
        return "    " + "\n    ".join([str(item[0]) + ": " + str(item[1]) for item in copy.items()])
