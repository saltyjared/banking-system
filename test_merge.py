

from banking_system_impl_241126_merge_account import BankingSystemImpl


def test_merge_accounts():

    banking_system = BankingSystemImpl()

    assert banking_system.create_account(1, "A1") == True
    assert banking_system.create_account(2, "A2") == True

    banking_system.deposit(3, "A1", 500)
    print(banking_system.accounts["A1"][-1][3])
    banking_system.deposit(4, "A2", 300)
    print(banking_system.accounts["A2"][-1][3])
    banking_system.pay(5, "A2", 100)
    print(banking_system.accounts["A2"][-1][3])

    assert "payment1" in banking_system.payments
    assert banking_system.payments["payment1"][0] == "A2"

    result = banking_system.merge_accounts(1000, "A1", "A2")
    assert result == True, "Account merge should succeed"

    assert "A2" not in banking_system.accounts, "A2 should no longer exist"
    assert len(banking_system.accounts["A1"]) > 2, "A1 should have A2's transactions merged"

    print(banking_system.accounts["A1"][-1][3]) # somehow this balance is 400, I don't know where is this value coming from
    assert banking_system.accounts["A1"][-1][3] == 700, "Balance should reflect merged accounts"

    assert banking_system.payments["payment1"][0] == "A1", "Cashback should now be credited to A1"

    top_spenders = banking_system.top_spenders(15, 1)
    assert "A1" in top_spenders[0], "A1 should be recognized as the top spender"

    assert banking_system.merge_accounts(20, "A1", "A1") == False, "Cannot merge the same account"
    assert banking_system.merge_accounts(20, "A1", "A3") == False, "Cannot merge with a non-existent account"

    print("All tests passed successfully!")

test_merge_accounts()
