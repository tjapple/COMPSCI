
from typing import Set
class Domain(Set[str]):
    def validate(self, value:str) -> str:
        if value in self:
            return value
        raise ValueError(f"invalid {value!r}")
species = Domain({"Iris-setosa", "Iris-versicolour", "Iris-virginica"})





from dataclasses import dataclass, asdict
from typing import Optional

@dataclass(frozen=True)
class Sample:
    sepal_length: float
    sepal_width: float
    petal_length: float
    petal_width: float

@dataclass(frozen=True)
class KnownSample(Sample):
    species: str

@dataclass
class TestingKnownSample:
    sample: KnownSample
    classification: Optional[str] = None

@dataclass(frozen=True)
class TrainingKnownSample:
    """Note: no classification instance variable available.
    EX: s1 = TrainingKnownSample(sample=KnownSample(sepal_length=5.1, sepal_width=, etc.))"""
    sample: KnownSample


class Sample:
    def __init__(self, sepal_length:float, sepal_width:float, petal_length:float, petal_width:float, species:Optional[str]=None,) -> None:
        self.sepal_length = sepal_length
        self.sepal_width = sepal_width
        self.petal_length = petal_length
        self.petal_width = petal_width
        self.species = species
        self.classification: Optional[str] = None

    def __repr__(self) -> str:
        if self.species is None:
            known_unknown = "UnknownSample"
        else:
            known_unknown = "KnownSample"
        if self.classification is None:
            classification = ""
        else: 
            classification = f", {self.classification}"
        return (
            f"{known_unknown}("
            f"sepal_length={self.sepal_length},"
            f"sepal_width={self.sepal_width},"
            f"petal_length={self.petal_length},"
            f"petal_width={self.petal_width},"
            f"species={self.species!r},"
            f"{classification}"
            f")"
        )
    @classmethod
    def from_dict(cls, row: dict[str,str]) -> "Sample":
        """Builds an intermediate representation of a Sample, validating its measurement attributes."""
        try:
            return cls(
                sepal_length=float(row["sepal_length"]),
                sepal_width=float(row["sepal_width"]),
                petal_length=float(row["petal_length"]),
                petal_width=float(row["petal_width"]),
                species = row["species"] #assign now and check in KnownSample class from_dict method
            )
        except ValueError as ex:
            raise InvalidSampleError(f"invalid {row!r}")
        except KeyError:
            raise InvalidSampleError(f"invalid key")
        


    def classify(self, classification:str) -> None:
        """Defines the state change from unclassified to classified.
        Setter method."""
        self.classification = classification
    
    def matches(self) -> bool:
        """Compares the results of classification with a Botanist-assigned species. Used for testing"""
        return self.species == self.classification

class UnknownSample(Sample): #DO I PUT SPECIES IN THE INIT???
    def __init__(self, sepal_length:float, sepal_width:float, petal_length:float, petal_width:float) -> None:
        super().__init__(
            sepal_length=sepal_length,
            sepal_width=sepal_width,
            petal_length=petal_length,
            petal_width=petal_width
        )
    def __repr__(self) -> str:
        return (f"{self.__class__.__name__}("
                f"sepal_length={self.sepal_length},"
                f"sepal_width={self.sepal_width},"
                f"petal_length={self.petal_length},"
                f"petal_width={self.petal_width},"
                f")"
        )
    @classmethod
    def from_dict(cls, row: dict[str,str]) -> "UnknownSample":
        sample = Sample.from_dict(row)
        return cls(
                species = None, #???? is this right?????
                sepal_length = sample.sepal_length,
                sepal_width = sample.sepal_width,
                petal_length = sample.petal_length,
                petal_width = sample.petal_width,
            )

class KnownSample(Sample):
    def __init__(self, species:str, purpose:int, sepal_length:float, sepal_width:float, petal_length:float, petal_width:float) -> None:
        purpose_enum = Purpose(purpose)
        if purpose_enum not in {Purpose.Training, Purpose.Testing}:
            raise ValueError(f"Invalid purpose: {purpose!r}: {purpose_enum}")
        super().__init__(
            sepal_length=sepal_length,
            sepal_width=sepal_width,
            petal_length=petal_length,
            petal_width=petal_width
        )
        self.species = species
        self.purpose = purpose_enum
        self._classification: Optional[str] = None

    def __repr__(self) -> str:
        return (f"{self.__class__.__name__}("
                f"sepal_length={self.sepal_length},"
                f"sepal_width={self.sepal_width},"
                f"petal_length={self.petal_length},"
                f"petal_width={self.petal_width},"
                f"species={self.species!r},"
                f")"
            )
    
    @property
    def classification(self) -> Optional[str]:
        if self.purpose == Purpose.Testing:
            return self._classification
        else:
            raise AttributeError(f"Training samples have no classification")
        
    @classification.setter
    def classification(self, value:str) -> None:
        if self.purpose == Purpose.Testing:
            self._classification = value
        else:
            raise AttributeError(f"Training samples cannot be classified")
        
    @classmethod
    def from_dict(cls, row: dict[str,str]) -> "KnownSample":
        """Will build an instance of this class if it passes checks."""
        sample = Sample.from_dict(row)
        try:

            return cls(
                species = species.validate(sample.species),
                sepal_length = sample.sepal_length,
                sepal_width = sample.sepal_width,
                petal_length = sample.petal_length,
                petal_width = sample.petal_width,
            )
        except ValueError as ex:
            raise InvalidSampleError(f"invalid {species!r}")
        
        #TODO keyerror, how to print which key is wrong
        #TODO handle extra keys
        #TODO handle upper and lower bounds. 
        
class TrainingKnownSample(KnownSample):
    pass
class TestingKnownSample(KnownSample):
    pass
        

@dataclass 
class Hyperparameter:
    """A specific tuning parameter set with k and a distance algorithm."""
    k: int
    algorithm: Distance
    data: weakref.ReferenceType["TrainingData"]

    def classify(self, sample:Sample) -> str:
        """The k-NN algorithm"""
        ...



class Hyperparameter:
    """A hyperparameter value and the overall quality of the classification."""
    def __init__(self, k:int, training:"TrainingData") -> None:
        self.k = k
        self.data: weakref.ReferenceType["TrainingData"] = weakref.ref(training)
        self.quality:float

    def test(self) -> None:
        """Run the entire test suite.
        Creates a quality score and saves it to this Hyperparameter instance. """
        training_data: Optional["TrainingData"] = self.data()
        if not training_data:
            raise RuntimeError("Broken weak reference")
        pass_count, fail_count = 0,0
        for sample in training_data.testing:
            sample.classification = self.classify(sample) #I dont understand where this classify() is coming from, what 'self' is calling it, and why it can pass in a "TrainingData" type
            if sample.mathces():
                pass_count += 1
            else: 
                fail_count += 1
        self.quality = pass_count / (pass_count + fail_count)

    def classify(self):
        #TODO runs the nearest neighbors algorithm
        pass


    

class TrainingData:
    """
    A set of training data and testing data with methods to load and test the samples.

    Has lists with 2 subclasses of Sample objects: KnownSample and UnknownSample.
    Also has a list with Hyperparameter instances. """

    def __init__(self, name:str) -> None:
        self.name = name
        self.uploaded: datetime.datetime
        self.tested: datetime.datetime
        self.training: List[Sample] = []
        self.testing: List[Sample] = []
        self.tuning: List[Hyperparameter] = []

    def load(self, raw_data_source: Iterable[dict[str,str]]) -> None:
        """Reads the raw data and partitions it into training and testing data, both instances of KnownSample."""
        bad_count = 0
        for n, row in enumerate(raw_data_source):
            try:
                if n % 5 == 0:
                    test = TestingKnownSample.from_dict(row)
                    self.testing.append(test)
                else:
                    train = TrainingKnownSample.from_dict(row)
                    self.training.append(train)
            except InvalidSampleError as ex:
                print(f"Row {n+1}: {ex}")
                bad_count += 1
        if bad_count != 0:
            print(f"{bad_count} invalid rows")
            return
        self.uploaded = datetime.datetime.now(tz=datetime.timezone=utc)

    def test(self, parameter: Hyperparameter) -> None:
        """Test this Hyperparameter value"""
        parameter.test() #Runs the hyperparameter test method. Creates a quality score for the Hyperparameter and stores it within that object instance. 
        self.tuning.append(parameter) #Stores the tested Hyperparameters into this list, so we can see how each parameter performed. 
        self.tested = datetime.datetime.now(tz=datetime.timezone.utc)

    def classify(self, parameter:Hyperparameter, sample:Sample) -> Sample:
        """Classify this sample"""
        classification = parameter.classify(sample) #yet to be defined
        sample.classify(classification) # simply stores the result of Hyperparameter's classify into the sample's attribute. This is a setter mthod. 
        return sample #PARAMETER.CLASSIFY IS BEING RUN TWICE. why don't we do sample.classify(classification) in the Hyperparameter.test()???????











class Purpose(enum.IntEnum):
    Classification = 0
    Testing = 1
    Training = 2