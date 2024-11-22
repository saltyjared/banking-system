from banking_system import BankingSystem

class BankingSystemImpl(BankingSystem):

    # Define number of milliseconds in a day for processing cashback operations
    MILLISECONDS_IN_1_DAY = 86400000

    def __init__(self):
        # Encapsulate registered accounts in a dictionary with account IDs as keys and balances as values
        self.accounts = {} # consider: a tuple with (timestamp, balance) to aid in level 4

        # implement a dictionary to track the transactions that occur 
        self.transactions = {} # need to make a dictionary of a list of tuples {account number : [(type_of_transaction, amount_transferred, timestamp)]}

        # Encapsulate scheduled cashbacks in a dictionary with {timestamp : (account_id, cashback_amount)}
        self.scheduled_cashbacks = {}

        # Track total number of payments made across banking system to give each payment a unique ID
        self.num_payments = 0

        # To consider: implement a merged_acocunts dictionary with mapping between primary and secondary accounts
        self.merged_accounts = {} #structure: {primary_account_id: secondary_account_id}

    # Level 1 
    def create_account(self, timestamp: int, account_id: str) -> bool:
        """
        Should create a new account with the given identifier if it
        doesn't already exist.
        Returns `True` if the account was successfully created or
        `False` if an account with `account_id` already exists.
        """
        # Edge case, account already exists in system
        if account_id in self.accounts:
            return False
        
        # Create new key in accounts and transactions dictionaries 
        self.accounts[account_id] = [(timestamp, 0)]
        self.transactions[account_id] = [] 
        return True
    
    def update_balance(self, account_id: str, type_of_transaction: str, amount: int, timestamp: int):
        prev_balance = self.accounts[account_id][-1][1]
        if type_of_transaction == 'Deposit':
            curr_balance = prev_balance + amount
        else:
            curr_balance = prev_balance - amount
        self.accounts[account_id].append((timestamp, curr_balance))
        return curr_balance

    def record_transaction(self, account_id: str, type_of_transaction: str, amount: int, timestamp: int) -> None:
        """
        Record each transaction for an account in the form
        of a tuple containing the transaction type, amount,
        and time.
        """
        self.transactions[account_id].append((type_of_transaction, amount, timestamp))

    def deposit(self, timestamp: int, account_id: str, amount: int) -> int | None:
        """
        Should deposit the given `amount` of money to the specified
        account `account_id`.
        Returns the balance of the account after the operation has
        been processed.
        If the specified account doesn't exist, should return
        `None`.
        """
        self.process_cashback(timestamp)

        # default implementation
        type_of_transaction = 'Deposit'
        if account_id not in self.accounts:
          return None
        else:
            self.record_transaction(account_id, type_of_transaction, amount, timestamp)
            #self.transactions[account_id].append((type_of_transaction, amount, timestamp))
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
        self.process_cashback(timestamp)

        if not source_account_id in self.accounts or not target_account_id in self.accounts \
            or source_account_id == target_account_id or self.accounts[source_account_id] < amount:
            return None

        self.accounts[target_account_id] += amount
        self.accounts[source_account_id] -= amount

        type_of_transaction = "Transfer"
        self.record_transaction(source_account_id, type_of_transaction, amount, timestamp)
        #self.transactions[source_account_id].append((type_of_transaction, amount, timestamp))
        return self.accounts[source_account_id]

    # Level 2
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
        outgoing_totals = {}

        for account_id, transactions in self.transactions.items():
            outgoing_total = 0
            for occurence in transactions:
                type_of_transaction, amount, timestamp = occurence[0], occurence[1], occurence[2]
                if type_of_transaction in ["Transfer", "Pay", "Withdraw"]: ### Check other transactions to add here  
                    outgoing_total += amount
            outgoing_totals[account_id] = outgoing_total

        sorted_accounts = sorted(outgoing_totals.items(), key= lambda x:(-x[1], x[0]))
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
    

    def process_cashback(self, timestamp: int) -> None:
        """
        Processes the cashback for a given timestamp.
        This function will be called first in every transaction
        function (deposit, pay, transfer) in order to process any
        standing cashbacks.
        """
        
        # List only cashback operations that are due at the current timestamp
        due_cashbacks = [t for t in self.scheduled_cashbacks.keys() if t <= timestamp]
        
        # Traverse through sorted cashback timestamps
        for cashback_timestamp in sorted(due_cashbacks):
            for account_id, cashback in self.scheduled_cashbacks[cashback_timestamp]:
                # Process cashback by adding to account balance and recording transaction
                self.accounts[account_id] += cashback
                self.record_transaction(account_id, 'Cashback', cashback, cashback_timestamp)
            # Delete entry in scheduled cashbacks to complete processing
            del self.scheduled_cashbacks[cashback_timestamp]

    def get_balance(self, timestamp: int, account_id: str, time_at: int) -> int | None:
        """
        Should return the total amount of money in the account
        `account_id` at the given timestamp `time_at`.
        If the specified account did not exist at a given time
        `time_at`, returns `None`.
          * If queries have been processed at timestamp `time_at`,
          `get_balance` must reflect the account balance **after** the
          query has been processed.
          * If the account was merged into another account, the merged
          account should inherit its balance history.
        """

        # Process cashback query before even accessing the balance 
        self.process_cashback(timestamp)
        # I also am unsure how we plan to implement an account merge, so I will hold off on that functionality
        if account_id not in self.accounts:
            return None
        elif account_id in self.merged_accounts:
            account = self.merged_accounts[account_id]
        else:
            account = account_id
        balance_updates = sorted(self.accounts[account], key=lambda x: x[0])
        balance_at_time = None
        for timestamp, _, _, balance in balance_updates:
            if timestamp > time_at:
                break
            balance_at_time = balance
        return balance_at_time
    
    def get_payment_status(self, timestamp: int, account_id: str, payment: str) -> str | None:
        """
        Should return the status of the payment transaction for the
        given `payment`.
        Specifically:
          * Returns `None` if `account_id` doesn't exist.
          * Returns `None` if the given `payment` doesn't exist for
          the specified account.
          * Returns `None` if the payment transaction was for an
          account with a different identifier from `account_id`.
          * Returns a string representing the payment status:
          `"IN_PROGRESS"` or `"CASHBACK_RECEIVED"`.
        """
        # default implementation

        # Check if account_id exists
        if account_id not in self.accounts:
          return None

        payment_number = int(payment.replace('payment',''))
        # Check if payment exists 

        if payment > self.num_payments:
            return None ## payment cannot exist if number of payments is greater than what is recorded
        
        exists = False

        for type_of_transaction, amount_transferred, timestamp_here in self.transactions[account_id]:
            if type_of_transaction == "Pay" and timestamp_here == timestamp:
                exists = True
                break

        if not exists:
            return None # payment does not exist
        
        cashback_due_time = timestamp + self.MILLISECONDS_IN_1_DAY
        if timestamp < cashback_due_time:
            return "IN_PROGRESS"
        else:
            return "CASHBACK_RECEIVED"

