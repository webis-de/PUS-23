from .account import Account
from csv import reader
    
class AccountList:
    """
    Wrapper class to collect accounts.

    Attributes:
        events: A map of Account objects with account_ids as keys.
    """
    def __init__(self, filepath):
        """
        Initialises the AccountList.

        Args:
            filepath: The path to the event CSV.
        """
        self.accounts = {}

        with open(filepath) as file:
            csv_reader = reader(file, delimiter=",")
            header = next(csv_reader)
            for row_number, row in enumerate(csv_reader, 1):
                try:
                    args = {header[i].strip():row[i].strip() for i in range(len(header))}
                    account = Account(args)
                    self.accounts[account.account_id] = account
                except ValueError:
                    print("Could not parse row " + str(row_number) + " in accounts: " + str(row))
