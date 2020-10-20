from .account import Account
from csv import reader
    
class AccountList:

    def __init__(self, filepath):

        self.accounts = []

        with open(filepath) as file:
            csv_reader = reader(file, delimiter=",")
            #skip header
            header = next(csv_reader)
            for row in csv_reader:
                try:
                    args = {header[i].strip():row[i].strip() for i in range(len(header))}
                    self.accounts.append(Account(**args))
                except ValueError:
                    print("Could not parse " + str(row))

    def get_account(self, account_id):
        for account in self.accounts:
            if account.account_id == account_id:
                return account
