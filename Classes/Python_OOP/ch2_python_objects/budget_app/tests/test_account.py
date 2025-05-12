import unittest
from budget.account import Account, InsufficientFundsError

class TestAccount(unittest.TestCase):
    def test_initial_balance(self):
        account = Account("Checking")
        self.assertEqual(account.get_balance(), 0.0)

    def test_deposit(self):
        account = Account("Checking")
        account.deposit(500)
        self.assertEqual(account.get_balance(), 500.0)

    def test_withdrawal_insufficient_funds(self):
        account = Account("Savings", 100)
        with self.assertRaises(InsufficientFundsError):
            account.withdraw(200)

if __name__ == "__main__":
    unittest.main()

    
