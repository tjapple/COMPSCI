



class SampleReader:
    """See iris.names for attribute ordering in bezdekIris.data file"""

    target_class = Sample
    header = [
        "sepal_length", "sepal_width", 
        "petal_length", "petal_width"
    ]

    def __init__(self, source:Path) -> None:
        self.source = source
    
    def sample_iter(self) -> Iterator[Sample]:
        target_class = self.target_class
        with self.source.open() as source_file:
            reader = csv.DictReader(source_file, self.header)
            for row in header:
                try:
                    sample = target_class(
                        sepal_length=float(row["sepal_length"]),
                        sepal_width=float(row["sepal_width"]),
                        petal_length=float(row["petal_length"]),
                        petal_width=float(row["petal_width"]),
                    )
                except ValueError as ex: #if the float raises the valueError, we map it to BadSampleError to distinguish from other parts in the code.
                    raise BadSampleRow(f"Invalid {row!r}") from ex
                yield sample


class SamplePartition(List[SampleDict], abc.ABC):
    """The overload decorators are telling mypy we want to override the different ways a List can be built.
    The * in the arguments separates parameters where the argument value can be provided positionally from params where the arg value
        must be provided as a keyword.
    The intent is to have this as the superclass and have subclasses be able to use data = SomeSamplePartition(data, training_subset=0.67).
     It extends the List class to provide two sub-lists. """
    @overload
    def __init__(self, *, training_subset:float=0.80) -> None:
        ...

    @overload
    def __init__(self, iterable:Optional[Iterable[SampleDict]]=None, *, training_subset:float=0.80) -> None:
        ...

    def __init__(self, iterable:Optional[Iterable[SampleDict]]=None, *, training_subset:float=0.80) -> None:
        self.training_subset = training_subset
        if iterable:
            super().__init__(iterable)
        else:
            super().__init__

    @abc.abstractproperty
    @property
    def training(self) -> List[TrainingKnownSample]:
        ...

    @abc.abstractmethod
    @property
    def testing(self) -> List[TestingKnownSample]:
        ...

class SampleDict(TypedDict):
    sepal_length: float
    sepal_width: float
    petal_length: float
    petal_width: float
    species: str


import random


class ShufflingSamplePartition(SamplePartition):
    """separating the training and testing data by shuffling and then cutting."""
    def __init__(self, iterable:Optional[Iterable[SampleDict]]=None, *, training_subset:float=0.80) -> None:
        super().__init__(iterable, training_subset=training_subset)
        self.split: Optional[int] = None

    def _shuffle(self) -> None:
        if not self.split:
            random.shuffle(self)
            self.split = int(len(self) * self.training_subset)

    @property
    def training(self) -> List[TrainingKnownSample]:
        self.shuffle()
        return [TrainingKnownSample(**sd) for sd in self[: self.split]]
    
    @property
    def testing(self) -> List[TestingKnownSample]:
        self.shuffle()
        return [TestingKnownSample(**sd) for sd in self[self.split :]]
    


class DealingPartition(abc.ABC):
    @abc.abstractmethod
    def __init__(self, items:Optional[Iterable[SampleDict]], *, training_subset:Tuple[int, int]=(8,10)) -> None:
        ...

    @abc.abstractmethod
    def extend(self, items:Iterable[SampleDict]) -> None:
        ...

    @abc.abstractmethod
    def append(self, item:SampleDict) -> None:
        ...

    @property
    @abc.abstractmethod
    def training(self) -> List[TrainingKnownSample]:
        ...

    @property
    @abc.abstractmethod
    def testing(self) -> List[TestingKnownSample]:
        ...


class CountingDealingPartition(DealingPartition):
    def __init__(self, items:Optional[Iterable[SampleDict]], *, training_subset:Tuple[int, int]=(8, 10)) -> None:
        self.training_subset = training_subset
        self.counter = 0
        self._training: List[TrainingKnownSample] = []
        self._testing: List[TestingKnownSample] = []
        if items:
            self.extend(items)

    def extend(self, items:Iterable[SampleDict]) -> None:
        for item in items:
            self.append(item)

    def append(self, item:SampleDict) -> None:
        n, d = self.training_subset
        if self.counter % d < n:
            self._training.append(TrainingKnownSample(**item))
        else:
            self._testing.append(TestingKnownSample(**item))
        self.counter += 1

    @property
    def training(self) -> List[TrainingKnownSample]:
        return self._training
    
    @property
    def testing(self) -> List[TestingKnownSample]:
        return self._testing
    



# Yet another way, using a higher-order function:
def training_80(s:KnownSample, i:int) -> bool:
    return i % 5 != 0

def training_75(s:KnownSample, i:int) -> bool:
    return i % 4 != 0

def training_67(s:KnownSample, i:int) -> bool:
    return i % 3 != 0

def partition(samples:Iterable[KnownSample], rule:Callable[[KnownSample, int], bool]) -> Tuple[TrainingList, TestingList]:
    """this implementation is nice and succinct, however, it passes through the data twice. """
    training_samples = [TrainingKnownSample(s) for i, s in enumerate(samples) if rule(s, i)]
    test_samples = [TestingKnownSample(s) for i, s in enumerate(samples) if not rule(s, i)]
    return training_samples, test_samples

def partition_1(samples:Iterable[KnownSample], rule:Callable[[KnownSample, int], bool]) -> Tuple[TrainingList, TestingList]:
    """this is better but does not handle duplicates."""
    training: TrainingList = []
    testing: TestingList = []

    for i, s in enumerate(samples):
        training_use = rule(s, i)
        if training_use:
            training.append(TrainingKnownSample(s))
        else:
            testing.append(TestingKnownSample(s))

    return training, testing

def partition_1p(samples:Iterable[KnownSample], rule:Callable[[KnownSample, int], bool]) -> Tuple[TrainingList, TestingList]:
    """I don't quite fully understand how the previous versions could potentially cause duplicate values.
    This one still would not garauntee no duplicates I guess. This algo will be revised further in Ch. 10, the Iterator Pattern.
    This partition algorithm should be integrated with the SampleReader class."""
    pools: defaultdict[bool, list[KnownSample]] = defaultdict(list)
    partition = ((rule(s, i), s) for i, s in enumerate(samples))
    for usage_pool, sample in partition:
        pools[usage_pool].append(sample)

    training = [TrainingKnownSample(s) for s in pools[True]]
    testing = [TestingKnownSample(s) for s in pools[False]]
    return training, testing



