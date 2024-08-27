import numpy as np


class GenericException(Exception):
    def __init__(self, message):
        self.message = message


# Return index of nda closest to value. nda (numpy.ndarray) must be 1d. If multiple occurrences should arise,
# the first is returned according to NumPy's argmin/max function.
def value_to_index(nda, value):
    diff = np.abs(nda - value)
    idx = np.argmin(diff)
    return idx
