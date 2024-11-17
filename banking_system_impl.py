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
    
    def pay(self, timestamp: int, account_id: str, amount: int) -> str | None:
        """
        Should withdraw the given amount of money from the specified
        account.
        All withdraw transactions provide a 2% cashback - 2% of the
        withdrawn amount (rounded down to the nearest integer) will
        be refunded to the account 24 hours after the withdrawal.
        If the withdrawal is successful (i.e., the account holds
        sufficient funds to withdraw the given amount), returns a
        string with a unique identifier for the payment transaction
        in this format:
        `"payment[ordinal number of withdraws from all accounts]"` -
        e.g., `"payment1"`, `"payment2"`, etc.
        Additional conditions:
          * Returns `None` if `account_id` doesn't exist.
          * Returns `None` if `account_id` has insufficient funds to
          perform the payment.
          * **top_spenders** should now also account for the total
          amount of money withdrawn from accounts.
          * The waiting period for cashback is 24 hours, equal to
          `24 * 60 * 60 * 1000 = 86400000` milliseconds (the unit for
          timestamps).
          So, cashback will be processed at timestamp
          `timestamp + 86400000`.
          * When it's time to process cashback for a withdrawal, the
          amount must be refunded to the account before any other
          transactions are performed at the relevant timestamp.
        """

        self.process_cashback(timestamp)
        
        # Edge case handling, returns None if account does not exist or balance less than payment amount
        if account_id not in self.accounts or self.accounts[account_id] < amount:
            return None
        
        # Process payment by subtracting from account balance and record transaction
        self.accounts[account_id] -= amount
        self.record_transaction(account_id, 'Pay', amount, timestamp)

        # Initialize cashback by calculating amount and storing in schedule
        cashback = amount * 2 // 100
        cashback_timestamp = timestamp + self.MILLISECONDS_IN_1_DAY
        if cashback_timestamp not in self.scheduled_cashbacks:
            self.scheduled_cashbacks[cashback_timestamp] = []
        self.scheduled_cashbacks[cashback_timestamp].append((account_id, cashback))

        # Increment number of payments to assign unique ID to payment
        self.num_payments += 1
        return 'payment' + str(self.num_payments)
    
    def merge_accounts(self, timestamp: int, account_id_1: str, account_id_2: str) -> bool:
        """
        Should merge `account_id_2` into the `account_id_1`.
        
        Returns `True` if accounts were successfully merged, or
        `False` otherwise. 
        Specifically:
          1. * Returns `False` if `account_id_1` is equal to
          `account_id_2`. -> 
          2. * Returns `False` if `account_id_1` or `account_id_2`
          doesn't exist. 

          3. * All pending cashback refunds for `account_id_2` should
          still be processed, but refunded to `account_id_1` instead. 
          
          4. * After the merge, it must be possible to check the status
          of payment transactions for `account_id_2` with payment
          identifiers by replacing `account_id_2` with `account_id_1`.

          5. * The balance of `account_id_2` should be added to the
          balance for `account_id_1`. *
          
          6. * `top_spenders` operations should recognize merged accounts
          - the total outgoing transactions for merged accounts should
          be the sum of all money transferred and/or withdrawn in both
          accounts.
          7. * `account_id_2` should be removed from the system after the
          merge.
        """
        # default implementation
        # 1 and 2
        if account_id_1 == account_id_2 or not account_id_1 in self.accounts or not account_id_2 in self.accounts:
            return False

        # 3
        for cashback_time, pending_cashbacks in list(self.scheduled_cashbacks.items()):
            updated_cashbacks = []
            for account_id, cashback_amount in pending_cashbacks:
                if account_id == account_id_2:
                    updated_cashbacks.append((account_id_1, cashback_amount))
                else:
                    updated_cashbacks.append((account_id, cashback_amount))
            self.scheduled_cashbacks[cashback_time] = updated_cashbacks

        # 4 
        if account_id_2 in self.transactions:
            if account_id_1 not in self.transactions:
                self.transactions[account_id_1] = []
            self.transactions[account_id_1].extend(self.transactions[account_id_2])
            del self.transactions[account_id_2]

        # 5
        self.accounts[account_id_1] += self.accounts[account_id_2]

        # 6 -> already achieved by merging the transaction record

        # 7
        del self.accounts[account_id_2]
