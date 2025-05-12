class InvalidSampleError(ValueError):
    """Source data file has invalid data representation"""

class OutlierError(ValueError):
    """Value lies outside the expected range."""

class BadSampleRow(ValueError):
    pass