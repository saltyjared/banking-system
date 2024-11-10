from banking_system import BankingSystem


class BankingSystemImpl(BankingSystem):

    def __init__(self):
        # TODO: implement
        pass

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




    # TODO: implement interface methods here


