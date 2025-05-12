from math import hypot

class Distance:
    """Definition of a distance computation"""
    def distance(self, s1:Sample, s2:Sample) -> float:
        pass


class ED(Distance):
    """Euclidean distance."""
    def distance(self, s1:Sample, s2:Sample) -> float:
        return hypot(
            s1.sepal_length - s2.sepal_length,
            s1.sepal_width - s2.sepal_width,
            s1.petal_length - s2.petal_length,
            s1.petal_width - s2.petal_width,
        )
    
class MD(Distance):
    """Manhattan distance. Sums the total distance between all points."""
    def distance(self, s1:Sample, s2:Sample) -> float:
        return sum(
            [
                abs(s1.sepal_length - s2.sepal_length),
                abs(s1.sepal_width - s2.sepal_width),
                abs(s1.petal_length - s2.petal_length),
                abs(s1.petal_wdith - s2.petal_width),
            ]
        )
    
class CD(Distance):
    """Chebyshev distance. Minimizes the effects of multiple dimensions. 
    Emphasizes neighbors that are closer to each other."""
    def distance(self, s1:Sample, s2:Sample) -> float:
        return max(
            [
                abs(s1.sepal_length - s2.sepal_length),
                abs(s1.sepal_width - s2.sepal_width),
                abs(s1.petal_length - s2.petal_length),
                abs(s1.petal_wdith - s2.petal_width),
            ]
        )
    
class SD(Distance):
    """Sorensen (aka Bray-Curtis) distance. Reduces the importance of measures that are further away from the origin."""
    def distance(self, s1:Sample, s2:Sample) -> float:
        return sum(
            [
                abs(s1.sepal_length - s2.sepal_length),
                abs(s1.sepal_width - s2.sepal_width),
                abs(s1.petal_length - s2.petal_length),
                abs(s1.petal_wdith - s2.petal_width),
            ]
        ) / sum(
            s1.sepal_length + s2.sepal_length,
            s1.sepal_width + s2.sepal_width,
            s1.petal_length + s2.petal_length,
            s1.petal_width + s2.petal_width,
        )

        )