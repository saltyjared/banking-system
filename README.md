# banking-system
<img src="https://th.bing.com/th/id/R.059119405ce24f00b354ad6a47179329?rik=hcu9USxTrd7Plg&pid=ImgRaw&r=0" alt="Banking system clipart" width="200"/>

## Overview
The following repository contains a comprehensive implementation of a banking system, built entirely of possible. The banking system is capable of many functionalities, such as account creation, performing transactions, account merging, and balance querying.

## Key Features
- Account creation and merging
- Chronological handling of operations
- Deposits, transfers, and payments
- Automatic 2% cashback payment processing
- Top spenders analysis
- Historical balance queries

## Attributes
- `accounts`: Record of each account in the banking system and their transaction histories.
- `payments`: Universal record of all payments made, identified by a unique payment ID. Stores information to properly handle and reimburse an automatic 2% cashback.
- `merged_accounts`: Record of which accounts have been merged and mapped to other accounts. Allows for proper handling of querying deprecated accounts to their new, merged account.

## Methods
- `create_account()`: Initializes a new bank account.
- `deposit()`: Adds funds to an account.
- `transfer()`: Moves money between accounts.
- `top_spenders()`: Analyzes and returns the highest spending accounts.
- `pay()`: Withdraw funds from account and schedules a 2% cashback payment.
- `get_payment_status()`: Returns status of a pending or completed cashback payment.
- `merge_accounts()`: Combines account histories.
- `get_balance()`: Retrieves account balance at a specific time.

## Dependencies
- `bisect`: Perform binary search to make historical balance queries.

## Usage Example
```
my_bank = BankingSystemImpl()

bank.create_account(1, 'acc1')
bank.create_account(2, 'acc2')

bank.deposit(3, 'acc1', 2000)
bank.deposit(4, 'acc2', 1200)

bank.transfer(5, 'acc2', 'acc1', 200)

bank.pay(6, 'acc1', 200) # returns 'payment1'
bank.get_payment_status(7, 'acc1', 'payment1') # returns 'IN_PROGRESS'

bank.top_spenders(8, 2) # returns ['acc1(200), acc2(200)']

bank.merge_accounts(9, 'acc1', 'acc2')
bank.get_balance(12, 'acc1', 10) # returns 3000

bank.get_balance(MILLISECONDS_IN_1_DAY + 10, 'acc1', MILLISECONDS_IN_1_DAY + 7) # returns 3004 (3000 + (0.02*400))

bank.get_payment_status(MILLISECONDS_IN_1_DAY + 11, 'acc1', 'payment1') # returns 'CASHBACK_RECEIVED'
```

### Developed by Rachana Baskar, Jared Guevara, Jaeyoon Jung, Shree Patel. 