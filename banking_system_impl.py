from banking_system import BankingSystem
import bisect

class BankingSystemImpl(BankingSystem):

    # Define number of milliseconds in a day for processing cashback operations
    MILLISECONDS_IN_1_DAY = 86400000

    def __init__(self):
        """
        Initializes banking system with empty dictionaries.
        1. {account_id : [(timestamp, transaction_type, amount, balance, account_id)]} 
        2. {payment_id : [account_id, timestamp, cashback, status]}
        3. {merged_account : active_account}

        Attributes
        ----------
        account: dict 
            Stores account's transaction history with account ID as key.
        payments: dict 
            Stores payment transaction information with payment ID as key. 
        merged_accounts: dict 
            Stores active account ID with merged, deactivated account ID as key. 
        """
        self.accounts = {}
        self.payments = {}
        self.merged_accounts = {}


    # Level 1 
    def create_account(self, timestamp: int, account_id: str) -> bool:
        """
        Create account if it does not already exist. 

        Parameters
        -----------
        timestamp: int 
            The timestamp at account creation. 
        account_id: str
            Unique identifier of new account.
        
        Returns
        --------
        bool 
            'True' if account was created successfully. 
            'False' if account already exists. 
        """

        # Edge case, account already exists in system
        if account_id in self.accounts:
            return False
        
        # Create new key in accounts and transactions dictionaries 
        self.accounts[account_id] = [(timestamp, "Account Creation", 0, 0, account_id)] 
        #print(f"{account_id} has been created at {timestamp}")
        return True

    def deposit(self, timestamp: int, account_id: str, amount: int) -> int | None:
        """
        Deposits a given amount into specified account ID and returns the new balance. 

        Parameters
        ----------
        timestamp: int 
            Timestamp of deposit. 
        account_id: str
            Account to which deposit is made. 
        amount: int 
            Amount to deposit.

        Returns 
        -------
        new_balance: int 
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
        prev_balance = self.accounts[account_id][-1][3] # Access most recent tuple's balance
        new_balance = prev_balance + amount
        self.accounts[account_id].append((timestamp, transaction_type, amount, new_balance, account_id))  
        #print(f"{account_id} has {new_balance}")   
        return new_balance
          
    def transfer(self, timestamp: int, source_account_id: str, target_account_id: str, amount: int) -> int | None:
        """
        Transfers specified amount from source account to target account. 

        Parameters
        ----------
        timestamp: int 
            Timestamp of transfer. 
        source_account_id: str
            Account from which transfer is made.
        target_account_id: str
            Account to which amount is transferred to. 
        amount: int 
            Amount to transfer.

        Returns 
        -------
        new_balance: int 
            New balance of source account after transfer. 
        None
            If transfer was invalid. 
        """
        
        # Process any due cashbacks prior to transfer
        self.process_cashback(timestamp)

        # Edge cases: either account not existing in system, source and target accounts are the same,
        # or source balance is less than amount
        if not source_account_id in self.accounts or not target_account_id in self.accounts \
            or source_account_id == target_account_id:
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
        self.accounts[source_account_id].append((timestamp, src_transaction_type, amount, new_src_balance, source_account_id))
        self.accounts[target_account_id].append((timestamp, tgt_transaction_type, amount, new_tgt_balance, target_account_id))
        #print(f"{source_account_id} has {new_src_balance}")   
        #print(f"{target_account_id} has {new_tgt_balance}")   
        return new_src_balance


    # Level 2
    def top_spenders(self, timestamp: int, n: int) -> list[str]:
        """
        Returns top `n` accounts with the highest outgoing transactions. 

        Parameters
        ----------
        timestamp: int 
            Timestamp at top_spenders evaluation.
        n: int 
            Number of accounts to output.

        Returns
        ----------
        output: list[str]
            List of account IDs and total outgoing transactions. 
            Format : ["account_id(amount)"].
        """
        
        # Initialize dictionary to hold account_id as keys and outgoing_total as values
        outgoing_totals = {}

        # Iterate through each account's history
        for account_id, transaction_history in self.accounts.items():
            # Initialize outgoing total to sum up each outgoing transaction amount
            outgoing_total = 0
            # Iterate through each transaction in one account's history
            for t in transaction_history:
                _, transaction_type, amount, _ = t[0], t[1], t[2], t[3] # Only type and amount are needed
                if transaction_type in ["Transfer Out", "Pay"]: # Only consider outgoing transactions  
                    outgoing_total += amount
            outgoing_totals[account_id] = outgoing_total

        # Sort outgoing_totals by largest outgoing_amount descending, then by account_id ascending (break ties)
        sorted_accounts = sorted(outgoing_totals.items(), key= lambda x:(-x[1], x[0]))
        output = [f"{account_id}({total})" for account_id, total in sorted_accounts[:n]]
        return output    


    # Level 3
    def pay(self, timestamp: int, account_id: str, amount: int) -> str | None:
        """
        Withdraws a given amount from a specified account. Provides a 2%
        cashback for every transaction, which is paid back after 24 hours.

        Parameters
        ----------
        timestamp: int 
            Timestamp of payment.
        account_id: str 
            Account from which payment is withdrawn from.
        amount: int
            Amount withdrawn.

        Returns
        ----------
        payment_id: str
            Unique identifier for each payment.
        None
            If account does not exist or account balance is less than amount.
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
        self.accounts[account_id].append((timestamp, transaction_type, amount, new_balance, account_id))

        # Initialize cashback by calculating amount and storing in schedule
        cashback = amount * 2 // 100
        cashback_timestamp = timestamp + self.MILLISECONDS_IN_1_DAY
        payment_id = 'payment' + str(len(self.payments) + 1)
        completed = False
        self.payments[payment_id] = [account_id, cashback_timestamp, cashback, completed]
        #print(f"{account_id} has {new_balance}")   
        return payment_id

    def process_cashback(self, timestamp: int) -> None:
        """
        Processes the cashback for a given timestamp.
        This function will be called first in every transaction
        function (deposit, pay, transfer) and getter function 
        (get_payment_status, get_balance) in order to process the
        cashback payment prior to these operations.

        Parameters
        ----------
        timestamp: int 
            Timestamp of current operation.

        Returns
        ----------
        None
        """
        
        # List only cashback operations that are due at the current timestamp
        # Timestamp will be the 2nd record in any payment value tuple
        due_cashbacks = sorted([payment_id for payment_id, value in self.payments.items() if value[1] <= timestamp])
        transaction_type = "Cashback"

        # Iterate through the the keys of due cashbacks
        for key in due_cashbacks:
            # Unpack the tuple associated with a due key
            account_id, cashback_timestamp, cashback, status = [*self.payments[key]]
            # Only process in progress cashbacks
            if not status:
                # Update balance and record transaction
                balance = self.accounts[account_id][-1][3]
                new_balance = balance + cashback
                self.accounts[account_id].append((cashback_timestamp, transaction_type, cashback, new_balance, account_id))
                status = True

            # Process payment by updating completed to be True
            self.payments[key] = [account_id, cashback_timestamp, cashback, status]

    def get_payment_status(self, timestamp: int, account_id: str, payment: str) -> str | None:
        """
        Returns the status of a cashback return for a given payment.
        
        Parameters
        ----------
        timestamp: int 
            Timestamp of checking status.
        account_id: str 
            Account from which payment was made.
        payment: str
            Unique ID for payment.

        Returns
        ----------
        str
            "CASHBACK_RECIEVED" if cashback was successfully processed and 
            added to account balance
            "IN_PROGRESS" if cashback has not been processed yet
        None
            If account or payment does not exist or if input account ID does not 
            match the account ID of the payment.
        """

        # Process any due cashback prior to getting payment status
        self.process_cashback(timestamp)

        # Check if account_id exists
        if account_id not in self.accounts or payment not in self.payments.keys():
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
    def merge_accounts(self, timestamp: int, account_id_1: str, account_id_2: str):
        """
        Merges `account_id_2` into `account_id_1`, combining their transaction
        histories and deleting `account_id_2` from the system.
        
        Parameters
        ----------
        timestamp: int 
            Timestamp of merge.
        account_id_1: str 
            Account being merged into, retaining the combined transaction
            history of both accounts.
        account_id_2: str
            Account being merged and deleted from the system.

        Returns
        ----------
        bool
            "True" if merge was completed successfully.
            "False" if both account IDs are the same or if either does not 
            exist in system.
        """
        # Edge cases: account IDs are the same or either does not exist in system
        if account_id_1 == account_id_2 or account_id_1 not in self.accounts or account_id_2 not in self.accounts:
            return False
                
        # Track accounts have been merged by adding key:val to dict
        self.merged_accounts[account_id_2] = account_id_1

        # Change all cashback payment history of account 2 to account 1
        for payment in self.payments.values():
            if payment[0] == account_id_2:
                payment[0] = account_id_1
        
        # Add balance of account 2 to account 1
        acc_2_bal = self.accounts[account_id_2][-1][3]
        acc_1_bal = self.accounts[account_id_1][-1][3]
        transaction_type = f'Merged Account with {account_id_2}'
        new_bal = acc_1_bal + acc_2_bal

        # Merge transaction histories of account 2 with account 1
        self.accounts[account_id_1].extend(self.accounts[account_id_2])
        self.accounts[account_id_1].sort()

        # Delete account 2 from system
        del self.accounts[account_id_2]

        # Record merge as a transaction for account 1
        self.accounts[account_id_1].append((timestamp, transaction_type, acc_2_bal, new_bal, account_id_1))

        return True
    
    def balance_query(self, timestamp: int, account_id: str, time_at: int, target_account) -> int | None:
        """
        Make a balance query based on merged account IDs that may be 
        deprecated. Performs a binary search to find the closest, passed
        timestamp to `time_at` to query balance from.

        Parameters
        ----------
        timestamp: int 
            Timestamp of query.
        account_id: str 
            Account from which balance is queried from.
        time_at: int
            Time of requested query.
        target_account: str
            Original account from which a transaction was made from. Can
            be from a deprecated account.

        Returns
        ----------
        int
            Balance of account at `time_at`.
        None
            If account does not exist.
        """

        # extract the account history 
        account_history = self.accounts[account_id]
        if not account_history:
            return None
        
        original_account_history = [x for x in account_history if x[4] == target_account]
    
        account_timestamps = [x[0] for x in original_account_history]
        closest_index = bisect.bisect_right(account_timestamps, time_at) - 1

        if closest_index == -1:
            return None

        #print(f"Debug: Starting balance_query for account {account_id} at time {time_at} targeting {target_account}")
        #print(f"Full account history: {account_history}")
        #print(f"Filtered account history for target account {target_account}: {original_account_history}")
        #print(f"Available timestamps: {account_timestamps}")
        #print(f"Closest index: {closest_index}, Closest timestamp: {account_timestamps[closest_index]}")

        return original_account_history[closest_index][3]

    def get_balance(self, timestamp: int, account_id: str, time_at: int) -> int | None:
        """
        Returns the total amount of money in an account at the given timestamp 
        `time_at`. Resolves queries dealing with merged accounts and combined
        transaction histories.

        Make a balance query based on merged account IDs that may be 
        deprecated. Performs a binary search to find the closest, passed
        timestamp to `time_at` to query balance from.

        Parameters
        ----------
        timestamp: int 
            Timestamp of query.
        account_id: str 
            Account from which balance is queried from.
        time_at: int
            Time of requested query.

        Returns
        ----------
        query: int
            Balance of account at `time_at`.
        None
            If account does not exist.
        """

        #print(f"Debug: Calling get_balance for account {account_id} at time {time_at} (current timestamp: {timestamp})")

        self.process_cashback(timestamp)

        target_account_id = account_id

        # if account ID does not exist, it must either be merged or non-existent
        if account_id not in self.accounts:

            # if the account id is not merged, then it must be non-existent
            if not account_id in self.merged_accounts:
                return None
            
            # if account id does exist in the merged dictionary, it has a new name now. we need to map the old_id to the new_id in the accounts dict, but query by the old_id
            else:

                # find new account id from dictionary mapping
                new_account_id = self.merged_accounts[account_id]

                # find the history of the new ID
                while new_account_id not in self.accounts:
                    account_id = new_account_id
                    new_account_id = self.merged_accounts[account_id]
                    
                new_history = self.accounts[new_account_id]

                # find the entry where the merge happened
                merge = [x for x in new_history if x[1] == f"Merged Account with {account_id}"]

                # find the timestamp of the merge
                merge_time = merge[0][0] if merge else None

                #print(f"Debug: New account ID for merged account {account_id} is {new_account_id}")
                #print(f"History for new account {new_account_id}: {new_history}")       

                # if the merge happened after the time we are querying, we want to access the old id for the result
                if merge_time > time_at:
                    #print(f"Merge happened at {merge_time}, which is after {time_at}. Querying old account {target_account_id}.")

                    query = self.balance_query(timestamp, new_account_id, time_at, target_account=target_account_id)
                    return query

                # if the merge happened before the time we are querying, then we are looking at shared history, and the merged account ID does not have this history anymore. 
                else: 
                    #print(f"Merge happened at {merge_time}, which is before {time_at}.")
                    return None

        # if the account ID is found in self.accounts, then it is not an account that has been merged with others 
        else: 

            # sort the entries by timestamp
            self.accounts[account_id].sort()

            # if the first entry in the account ID is after the query time, this account didn't exist
            if self.accounts[account_id][0][0] > time_at:
                return None

            # extract the account history
            account_history = self.accounts[account_id]

            # if there is no history
            if not account_history:
                return None
            
            #print(f"Debug: Found account {account_id}. Full history: {self.accounts[account_id]}")
            #print(f"Querying account {account_id} at time {time_at} for balance.")
            
            # query
            query = self.balance_query(timestamp, account_id, time_at, target_account=account_id)

            return query