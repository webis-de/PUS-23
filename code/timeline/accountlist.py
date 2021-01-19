from .account import Account
from csv import reader
    
class AccountList:

    def __init__(self, filepath):

        self.accounts = {}

        with open(filepath) as file:
            csv_reader = reader(file, delimiter=",")
            #skip header
            header = next(csv_reader)
            for row_number, row in enumerate(csv_reader, 1):
                try:
                    args = {header[i].strip():row[i].strip() for i in range(len(header))}
                    account = Account(args)
                    self.accounts[account.account_id] = account
                except ValueError:
                    print("Could not parse row " + str(row_number) + " in accounts: " + str(row))
