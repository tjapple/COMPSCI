### Str/Repr ###
\_\_str\_\_ is the user-friendly representation. Define what you want printed when you call print(obj)

\_\_repr\_\_ is the developer version. Define it like this: f"\<Classname\>(arg1={self.arg1}, arg2={self.arg2})

-good practice to use both

### Doctest in Docstrings ###
-write examples in the docstring so doctest can pick up on them, formatted like this:
```python
"""description of method.

>>> acc = Account('savings', 100)
>>> acc.depost(50)
>>> acc._balance
150
"""
```

### unittest.TestCase ###
-provides all the assert statements
-finds and automatically runs any method prefixed with test_
