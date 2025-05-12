\_\_str\_\_ is the user-friendly representation. Define what you want printed when you call print(obj)

\_\_repr\_\_ is the developer version. Define it like this: f"\<Classname\>(arg1={self.arg1}, arg2={self.arg2})

-good practice to use both




-write examples in the docstring so doctest can pick up on them, formatted like this:
"""description of method.

>>> acc = Account('savings', 100)
>>> acc.depost(50)
>>> acc._balance
150
"""
