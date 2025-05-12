class MediaLoader(abc.ABC):
    @abc.abstractmethod
    def play(self) -> None:
        ...

    @property
    @abc.abstractmethod
    def ext(self) -> str:
        ...

###############################
###############################
###############################
import abc

class Die(abc.ABC):
    def __init__(self) -> None:
        self.face: int
        self.roll()

    @abc.abstractmethod
    def roll(self) -> None:
        ...

    def __repr__(self) -> str:
        return f"{self.face}"
    
    def __mul__(self, n:int) -> "DDice":
        for _ in range(n):
            DDice(type(self))
            #TODO
    def __rmul__(self, n:int) -> "DDice":
        #TODO
    
class D4(Die):
    def roll(self) -> None:
        self.face = random.choice((1,2,4,5))

class D6(Die):
    def roll(self) -> None:
        self.face = random.randint(1,6)


class Dice(abc.ABC):
    def __init__(self, n:int, die_class:Type[Die]) -> None:
        self.dice = [die_class() for _ in range(n)]

    @abc.abstractmethod
    def roll(self) -> None:
        ...

    @property
    def total(self) -> int:
        return sum(d.face for d in self.dice)
    
class SimpleDice(Dice):
    def roll(self) -> None:
        for d in self.dice:
            d.roll()

class YachtDice(Dice):
     """EX: sd = YachtDice()
    sd.roll()
    sd.dice
    >>> [2,2,2,6,1]
    sd.saving([0,1,2]).roll()
    sd.dice
    >>> [2,2,2,2,6]"""
    def __init__(self) -> None:
        super().__init__(5, D6)
        self.saved: Set[int] = set()

    def saving(self, positions:Iterable[int]) -> "YachtDice":
        if not all(0 <= n < 6 for n in positions):
            raise ValueError("Invalid position")
        self.saved = set(positions)
        return self
    
    def roll(self) -> None:
        for n, d in enumerate(self.dice):
            if n not in self.saved:
                d.roll()
            self.saved = set()



class DDice:
    """represents a handful of dice. It is immutable, so each operation returns a new DDice object."""
    def __init__(self, *die_class:Type[Die]) -> None:
        self.dice = [dc() for dc in die_class]
        self.adjust: int = 0

    def plus(self, adjust:int = 0) -> "DDice":
        self.adjust = adjust
        return self
    
    def roll(self) -> None:
        for d in self.dice:
            d.roll()

    @property
    def total(self) -> int:
        return sum(d.face for d in self.dice) + self.adjust
    
    def __add__(self, die_class:Any) -> "DDice":
        if isinstance(die_class, type) and issubclass(die_class, Die):
            new_classes = [type(d) for d in self.dice] + [die_class]
            new = DDice(*new_classes).plus(self.adjust)
            return new
        elif isinstance(die_class, int):
            new_classes = [type(d) for d in self.dice]
            new = DDice(*new_classes).plus(die_class)
            return new
        else: 
            return NotImplemented
        
    def __radd__(self, die_class:Any) -> "DDice": 
        """this allows for the commutative property."""
        if isinstance(die_class, type) and issubclass(die_class, Die):
            new_classes = [die_class] + [type(d) for d in self.dice] 
            new = DDice(*new_classes).plus(self.adjust)
            return new
        elif isinstance(die_class, int):
            new_classes = [type(d) for d in self.dice]
            new = DDice(*new_classes).plus(die_class)
            return new
        else: 
            return NotImplemented


############################################
# Changing the metaclass of the Die implementations

import logging
from functools import wraps
from typing import Type, Any

class DieMeta(abc.ABCMeta):
    """The metaclass parameter is just a reference to the metaclass doing the work.
    The name parameter is the name of the target class, taken from the original class statement.
    The bases param is the list of base classes. 
    The namespace param is a dict that was started by the __prepare__() method of the built-in type class. 
        This was updated when the class body was executed. 
    """
    def __new__(metaclass:Type[type], name:str, bases:tuple[type, ...], namespace:dict[str, Any], **kwargs:Any) -> "DieMeta":
        # Check if class has a concrete roll() method
        if "roll" in namespace and not getattr(namespace["roll"], "__isabstractmethod__", False):
            namespace.setdefault("logger", logging.getLogger(name)) #adds logger to namespace
            original_method = namespace["roll"]

            @wraps(original_method)
            def logged_roll(self:"DieLog") -> None:
                original_method(self)
                self.logger.info(f"Rolled {self.face}")

            namespace["roll"] = logged_roll

        new_object = cast("DieMeta", abc.ABCMeta.__new__(metaclass, name, bases, namespace))
        return new_object

class DieLog(metaclass=DieMeta):
    """this superclass is built by the metaclass. Any subclass of this will also be built by the metaclass. 
    Subclassing EX: 
    class D6L(DieLog):
        ...
        """
    logger: logging.Logger

    def __init__(self) -> None:
        self.face: int
        self.roll()

    @abc.abstractmethod
    def roll(self) -> None:
        ...

    def __repr__(self) -> str:
        return f"{self.face}"


######################################
######################################
#######################################
# Creating a new dict type that doesn't update keys once loaded in.
from __future__ import annotations
from typing import cast, Union, Tuple, Dict, Hashable, Any, Mapping, Iterable
from collections import Hashable

DictInit = Union[
    Iterable[Tuple[Hashable, Any]],
    Mapping[Hashable, Any], 
    None]

class NoDupDict(Dict[Hashable, Any]):
    def __setitem__(self, key:Hashable, value:Any) -> None:
        if key in self:
            raise ValueError(f"duplicate {key!r}")
        super().__setitem__(key, value)
    #__setitem__ solves the problem for adding keys, but not for initializing already-created dicts, so we need to update __init__ as well

    def __init__(self, init:DictInit = None, **kwargs:Any) -> None:
        if isinstance(init, Mapping):
            super().__init__(init, **kwargs)
        elif isinstance(init, Iterable):
            for k, v in cast(Iterable[Tuple[Hashable, Any]], init):
                self[k] = v
        elif init is None:
            super().__init__(**kwargs)
        else:
            super().__init__(init, **kwargs)

    # We still would have to update all methods that can update a mapping: update(), setdefault(), __or__(), __ior__()
        