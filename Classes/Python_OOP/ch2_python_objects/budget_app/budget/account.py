class Account:
    def __init__(self, name: str, initial_balance: float = 0.0):
        self.name = name
        self._balance = initial_balance

    def deposit(self, amount: float) -> None:
        """Add money to an account.
        >>> acc = Account('checking', 100)
        >>> acc.deposit(100)
        >>> acc.get_balance
        200
        """

        if amount <= 0:
            raise ValueError("Deposit must be positive")
        self._balance += amount

    def withdraw(self, amount: float) -> None:
        """Take out money from an account.
        >>> acc = Account('checking', 100)
        >>> acc.withdraw(50)
        >>> acc.get_balance
        50
        """
        if amount <= 0:
            raise ValueError("Deposit must be positive")
        if amount > self._balance:
            raise InsufficientFundsError("Insufficient Funds")
        else:
            self._balance -= amount

    def get_balance(self) -> float:
        """Return the current balance of an account."""
        return self._balance
    
    def __str__(self) -> str:
        return f"{self.name}: {self._balance}"
    
    def __repr__(self) -> str:
        return f"Account(name={self.name}, balance={self._balance})"
    
    
class InsufficientFundsError(ValueError):
    """Not enough funds in the account for this withdrawal."""
    pass


