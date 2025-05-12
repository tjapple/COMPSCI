from budget.account import Account, InsufficientFundsError

def main():
    checking = Account("Checking")
    savings = Account("Savings")

    checking.deposit(5000)

    try: 
        savings.withdraw(500)
    except InsufficientFundsError as e:
        print(f"Withdrawal failed: {e}")


    print(checking)
    print(savings)

    


if __name__ == "__main__":
    main()