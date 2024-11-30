from banking_system import BankingSystem


class BankingSystemImpl(BankingSystem):

    # Define number of milliseconds in a day for processing cashback operations
    MILLISECONDS_IN_1_DAY = 86400000

    def __init__(self):
        """
        Initializes banking system with empty dictionaries.
        1. {Accounts : [(time, transaction_type, amount, balance)]} 
        2. {Payment : [(account, timestamp, cashback, status)]}
        3. {Merged_Account : []}

        Attributes
        ----------
        account : dict 
            Stores account's transaction histrory with account ID as key.
        payments : dict 
            Stores payment transactions + cashback scheduled with payment ID as key. 
        merged_accounts : dict 
            Stores merged account IDs to new account ID. 
        """
        self.accounts = {}
        self.payments = {}
        self.merged_accounts = {} # Not needed right??
    
    def create_account(self, timestamp: int, account_id: str) -> bool:
        """
        Create account if it does not already exisit. 

        Parameters
        -----------
        timestamp : int 
            The timestamp at account creation. 
        account_id : str
            Unique identifier of new account.
        Returns
        --------
        bool 
            'True' if account created successfully. 
            'False' if account already exists. 
        """

        # Edge case, account already exists in system
        if account_id in self.accounts:
            return False

        # Create new key in accounts and transactions dictionaries
        self.accounts[account_id] = [(timestamp, "Account Creation", 0, 0)]
        return True

    def deposit(self, timestamp: int, account_id: str, amount: int) -> int | None:
        """
        Deposits a given amount into specified account ID and returns new balance. 

        Parameters
        ----------
        timestamp : int 
            Timestamp of deposit. 
        account_id : str
            Acount to which deposit is made. 
        amount : int 
            Amount to deposit

        Returns 
        -------
        new_balance : int 
            New balance of account after deposit. 
        None
            If account does not exist. 
        """

        # Process any due cashbacks prior to deposit
        self.process_cashback(timestamp)

        # Edge case: account does not exist in system
        if account_id not in self.accounts:
            return None

        # Add amount to account balance and update record
        transaction_type = "Deposit"
        prev_balance = self.accounts[account_id][-1][3] 
        # Access most recent tuple's balance
        new_balance = prev_balance + amount
        self.accounts[account_id].append(
            (timestamp, transaction_type, amount, new_balance)
        )
        return new_balance

    def transfer(self, timestamp: int, source_account_id: str, target_account_id: str, amount: int) -> int | None:
        """
        Transfers specified amount from source account to target account. 

        Parameters
        ----------
        timestamp : int 
            Timestamp of transfer. 
        source_account_id : str
            Acount from which transfer is made.
        target_account_id : str
            Acount to which amount is transferredd to. 
        amount : int 
            Amount to transfer.

        Returns 
        -------
        new_balance : int 
            New balance of source account after transfer. 
        None
            If transfer was invalid. 
        """

        # Process any due cashbacks prior to transfer
        self.process_cashback(timestamp)

        if (
            # Account not existing in system 
            not source_account_id in self.accounts
            # Source_account same as target_account
            or target_account_id not in self.accounts
            # Source balance is less than amount
            or source_account_id == target_account_id
        ):
            return None

        # Define src_balance after checking source_account_id exists and ensure it is larger than amount
        src_balance = self.accounts[source_account_id][-1][3]
        if src_balance < amount:
            return None

        # Perform transfer by subtracting amount from source balance and adding amount to target balance
        src_transaction_type = "Transfer Out"
        tgt_transaction_type = "Transfer In"
        tgt_balance = self.accounts[target_account_id][-1][3]
        new_src_balance = src_balance - amount
        new_tgt_balance = tgt_balance + amount

        # Record transactions in each account's history
        self.accounts[source_account_id].append(
            (timestamp, src_transaction_type, amount, new_src_balance)
        )
        self.accounts[target_account_id].append(
            (timestamp, tgt_transaction_type, amount, new_tgt_balance)
        )
        return new_src_balance

    def top_spenders(self, timestamp: int, n: int) -> list[str]:
        """
        Returns top `n` accounts with the highest outgoing transactions. 

        Parameters
        ---------
        timestamp : int 
            Timestamp at top_spenders evaluation.
        n: int 
            Number of accounts to output

        Returns
        ----------
        output: list[str]
            List of account IDs and total outgoing transactions. 
            Format : ["account_id(amount)"].
        """

        # Initialize dictionary with account_id as keys and outgoing_total as values
        outgoing_totals = {}

        # Iterate through each account's history
        for account_id, transaction_history in self.accounts.items():
            # Initialize outgoing total to sum up each outgoing transaction amount
            outgoing_total = 0
            # Iterate through each transaction in one account's history
            for t in transaction_history:
                transaction_type, amount = t[1], t[2]  # Only type and amount are needed
                if transaction_type in [
                    "Transfer Out",
                    "Pay",
                ]:  # Only consider outgoing transactions
                    outgoing_total += amount
            outgoing_totals[account_id] = outgoing_total

        # Sort outgoing_totals by largest outgoing_amount descending, then by account_id ascending (break ties)
        sorted_accounts = sorted(outgoing_totals.items(), key=lambda x: (-x[1], x[0]))
        output = [f"{account_id}({total})" for account_id, total in sorted_accounts[:n]]
        return output

    # Level 3
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

        # Process any due cashback prior to payment
        self.process_cashback(timestamp)

        # Edge cases: account does not exist or balance less than payment amount
        if account_id not in self.accounts:
            return None
        balance = self.accounts[account_id][-1][3]
        if balance < amount:
            return None

        # Process payment by subtracting from account balance and record transaction
        transaction_type = "Pay"
        new_balance = balance - amount
        self.accounts[account_id].append(
            (timestamp, transaction_type, amount, new_balance)
        )

        # Initialize cashback by calculating amount and storing in schedule
        cashback = amount * 2 // 100
        cashback_timestamp = timestamp + self.MILLISECONDS_IN_1_DAY
        payment_id = "payment" + str(len(self.payments) + 1)
        completed = False
        self.payments[payment_id] = (
            account_id,
            cashback_timestamp,
            cashback,
            completed,
        )
        return payment_id

    def process_cashback(self, timestamp: int) -> None:
        """
        Processes the cashback for a given timestamp.
        This function will be called first in every transaction
        function (deposit, pay, transfer) in order to process any
        standing cashbacks.
        """

        # List only cashback operations that are due at the current timestamp
        # Timestamp will be the 2nd record in any payment value tuple
        due_cashbacks = sorted(
            [
                payment_id
                for payment_id, value in self.payments.items()
                if value[1] <= timestamp
            ]
        )
        transaction_type = "Cashback"

        # Iterate through the the keys of due cashbacks
        for key in due_cashbacks:
            # Unpack the tuple associated with a due key
            account_id, cashback_timestamp, cashback, status = self.payments[key]
            # Only process in progress cashbacks
            if not status:
                # Update balance and record transaction
                balance = self.accounts[account_id][-1][3]
                new_balance = balance + cashback
                self.accounts[account_id].append(
                    (cashback_timestamp, transaction_type, cashback, new_balance)
                )
                status = True

            # Process payment by updating completed to be True
            self.payments[key] = (account_id, cashback_timestamp, cashback, status)

    def get_payment_status(
        self, timestamp: int, account_id: str, payment: str
    ) -> str | None:
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

        # Process any due cashback prior to getting payment status
        self.process_cashback(timestamp)

        # Check if account_id exists
        if account_id not in self.accounts or payment not in self.payments:
            return None

        # If account exists, check if account_id of payment matches input
        payment_info = self.payments[payment]
        payment_account_id = payment_info[0]

        if account_id != payment_account_id:
            return None

        status = payment_info[3]
        if status:
            return "CASHBACK_RECEIVED"
        elif not status:
            return "IN_PROGRESS"

    # Level 4
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

        self.process_cashback(timestamp)
        if account_id not in self.accounts:
            return None
        elif account_id in self.merged_accounts:  ####
            account = self.merged_accounts[account_id]  ####
        else:
            account = account_id
        balance_updates = sorted(self.accounts[account], key=lambda x: x[0])
        balance_at_time = None
        for timestamp, _, _, balance in balance_updates:
            if timestamp > time_at:
                break
            balance_at_time = balance
        return balance_at_time

    def merge_accounts(
        self, timestamp: int, account_id_1: str, account_id_2: str
    ) -> bool:
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
        """      
        1. * Returns `False` if `account_id_1` is equal to
          `account_id_2`. -> 
          """
        if account_id_1 == account_id_2:
            return False

        """
        2. * Returns `False` if `account_id_1` or `account_id_2`
          doesn't exist. 
        """
        if account_id_1 not in self.accounts or account_id_2 not in self.accounts:
            return False

        self.process_cashback(timestamp)

        # 3 Processing pending cashbacks for accoutn 2 and transfer --> account 1
        """     
        3. * All pending cashback refunds for `account_id_2` should
          still be processed, but refunded to `account_id_1` instead. 
        """
        for payment_id, (account, cashback_timestamp, cashback, status) in list(
            self.payments.items()
        ):
            if account == account_id_2 and status is False:
                self.payments[payment_id] = (
                    account_id_1,
                    cashback_timestamp,
                    cashback,
                    status,
                )

        # 4 Merge transaction histories
        self.accounts[account_id_1].extend(self.accounts[account_id_2])

        # Combine balances
        balance_account_1 = self.accounts[account_id_1][-1][3]
        balance_account_2 = self.accounts[account_id_2][-1][3]
        combined_balance = balance_account_1 + balance_account_2
        self.accounts[account_id_1][-1] = (
            timestamp,
            "Account Merged",
            0,
            combined_balance,
        )
        del self.accounts[account_id_2]
        self.merged_accounts[account_id_2] = account_id_1
        return True
