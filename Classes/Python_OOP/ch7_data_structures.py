s = ("AAPL", 123.52, 53.15, 137.98)
def high(stock):
    symbol, current, high, low = stock
    return high
#instead of this:
s[2]
#do this:
high(s)


########################
#NamedTuple example
from typing import NamedTuple
class Stock(NamedTuple):
    symbol:str
    current:float
    high:float
    low:float

    @property
    def middle(self) -> float:
        return (self.high + self.low) / 2

Stock("AAPL", 123.52, 53.15, 137.98)
s2 = Stock("AAPL", 123.52, high=53.15, low=137.98)
s2.high
s2.middle


########################
# Dataclass example
from dataclasses import dataclass
@dataclass
class Stock:
    symbol:str
    current:float
    high:float
    low:float

s = Stock("AAPL", 123.52, 53.15, 137.98)
s.current
s.current = 111.11
s.unexpected_attribute = 'allowed'

#For comparison, here is an ordinary class that is similar:
class StockOrdinary:
    def __init__(self, name:str, current:float, high:float, low:float) -> None:
        self.name = name
        self.current = current
        self.high = high
        self.low = low

#defuaults and ordering
@dataclass(order=True)
class StockOrdered:
    name:str
    current:float = 0.0
    high:float = 0.0
    low:float = 0.0

