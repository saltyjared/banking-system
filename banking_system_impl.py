from banking_system import BankingSystem


class BankingSystemImpl(BankingSystem):

    def __init__(self):
        # Encapsulate registered accounts as a hashmap/dictionary with account IDs as keys and balances as 
        self.accounts = {}

        # implement a dictionary to track the transactions that occur 
        self.transactions = {}

    # TODO: implement interface methods here
    def create_account(self, timestamp, account_id):
        if account_id in self.accounts:
            return False
        self.accounts[account_id] = 0
        return True

    def top_spenders(self, timestamp: int, n: int) -> list[str]:
        """
        Return the id and outgoing transactions of the top `n` accounts with the highest outgoing transactions 

        Parameters
        ---------
        n: int 
            number of accounts to output

        Returns
        ----------
        output: list[str]
            list of n strings with the top id's and transaction sums
        """
        output = []
        outgoing_totals = {}

        # check if there are less than n accounts
        if len(self.accounts) < n: 
            for id in self.accounts.keys():

                # assuming I have a list of transactions 
                outgoing_totals[id] = sum(self.transactions[id])
                output.append(f"{id}({outgoing_totals[id]})")
        else:
            for id in self.accounts.keys():

                # assuming I have a list of transactions
                outgoing_totals[id] = sum(self.transactions[id])
            
            sorted_accounts = sorted(outgoing_totals.items(), key = lambda x: (-x[1], x[0]))
            output = [f"{account_id}({total})" for account_id, total in sorted_accounts[:n]]
        return output
