from banking_system import BankingSystem


class BankingSystemImpl(BankingSystem):

    def __init__(self):
        # Encapsulate registered accounts as a hashmap/dictionary with account IDs as keys and balances as 
        self.accounts = {}

        # implement a dictionary to track the transactions that occur 
        self.transactions = {}

    def deposit(self, timestamp: int, account_id: str, amount: int) -> int | None:
        """
        Should deposit the given `amount` of money to the specified
        account `account_id`.
        Returns the balance of the account after the operation has
        been processed.
        If the specified account doesn't exist, should return
        `None`.
        """
        # default implementation
              
        if account_id not in self.accounts:
          return None
        else: 
          self.accounts[account_id] += amount # Add to balances in account id
          return self.accounts[account_id]
        
    def transfer(self, timestamp: int, source_account_id: str, target_account_id: str, amount: int) -> int | None:
        """
        Should transfer the given amount of money from account
        `source_account_id` to account `target_account_id`. 
        Returns the balance of `source_account_id` if the transfer
        was successful or `None` otherwise.
          * Returns `None` if `source_account_id` or
          `target_account_id` doesn't exist.
          * Returns `None` if `source_account_id` and 
          `target_account_id` are the same.
          * Returns `None` if account `source_account_id` has 
          insufficient funds to perform the transfer.
        """

        # self.accounts = {} -> key: account id / value: funds

        # default implementation
        if not source_account_id in self.accounts or not target_account_id in self.accounts \
            or source_account_id == target_account_id or self.accounts[source_account_id] < amount:
            return None

        self.accounts[target_account_id] += amount
        self.accounts[source_account_id] -= amount

        return self.accounts[source_account_id]


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
    
    def merge_accounts(self, timestamp: int, account_id_1: str, account_id_2: str) -> bool:
        """
        Should merge `account_id_2` into the `account_id_1`.
        Returns `True` if accounts were successfully merged, or
        `False` otherwise.
        Specifically:
          * Returns `False` if `account_id_1` is equal to
          `account_id_2`. -> 
          * Returns `False` if `account_id_1` or `account_id_2`
          doesn't exist.
          * All pending cashback refunds for `account_id_2` should
          still be processed, but refunded to `account_id_1` instead. ***** 뭔소리지
          * After the merge, it must be possible to check the status
          of payment transactions for `account_id_2` with payment
          identifiers by replacing `account_id_2` with `account_id_1`.
          * The balance of `account_id_2` should be added to the
          balance for `account_id_1`.
          * `top_spenders` operations should recognize merged accounts
          - the total outgoing transactions for merged accounts should
          be the sum of all money transferred and/or withdrawn in both
          accounts.
          * `account_id_2` should be removed from the system after the
          merge.
        """
        # default implementation
        if account_id_1 == account_id_2 or not account_id_1 in self.accounts or not account_id_2 in self.accounts:
            return False
        


        