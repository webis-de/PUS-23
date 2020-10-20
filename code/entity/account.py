class Account:

    def __init__(self, account_id, url, type, genre, dynamic, account_year, account_month, account_day, about, bib_keys, publisher_author):

        self.account_id = account_id
        self.url = url
        self.type = type
        self.genre = genre
        self.dynamic = dynamic
        self.account_year = account_year
        self.account_month = account_month
        self.account_day = account_day
        self.account_date = self.get_account_date()
        self.about = about
        self.bib_keys = bib_keys
        self.publisher_author = publisher_author

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
