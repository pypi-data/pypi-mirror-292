# Copyright (c) 2024 Bartłomiej Kizielewicz

__all__ = [
    'FuzzyNormalization',
]


class FuzzyNormalization:
    """ Class for applying a series of fuzzy normalization functions to decision matrices.

        Parameters
        ----------
        fuzzy_numbers : list[callable]
            A list of functions representing the fuzzy numbers to be used for normalization.
    """

    def __init__(self, fuzzy_numbers):
        self.fuzzy_numbers = fuzzy_numbers
        self.iterator = iter(self.fuzzy_numbers)

    def __call__(self, matrix, *args, **kwargs):
        """ Normalize the decision matrix using the next fuzzy number in the sequence.

            Parameters
            ----------
            matrix : ndarray
                The decision matrix to be normalized.

            Returns
            -------
            ndarray
                The normalized decision matrix.
        """
        try:
            fuzzy_number = next(self.iterator)
        except StopIteration:
            self.iterator = iter(self.fuzzy_numbers)
            fuzzy_number = next(self.iterator)

        return fuzzy_number(matrix)
