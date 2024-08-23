# Copyright (c) 2024 Bartłomiej Kizielewicz

import numpy as np


class MLExpert:
    """ Create an object which will rate characteristic objects using ml expert function.

        Parameters
        ----------
            expert_function : Callable
                Function with a signature (co_i, co_j) -> float.
                If co_i < co_j this function should return 0.0.
                If co_i == co_j this function should return 0.5.
                If co_i > co_j this function should return 1.0.
    """
    def __init__(self, expert_function, reverse=False):
        self.expert_function = expert_function
        self.reverse = reverse

    def __call__(self, co):
        """ Evaluate characteristic objects using provided expert function.

            Parameters
            ----------
            co : np.ndarray
                Characteristic objects which should be compared.

            Returns
            -------
                sj : np.ndarray
                    SJ vector (see the COMET procedure for more info).

                mej : None
                    Because of how this method works MEJ matrix is not
                    generated.
        """
        mej = np.diag(np.ones(co.shape[0]) * 0.5)
        for i in range(mej.shape[0]):
            for j in range(i + 1, mej.shape[0]):
                v = self.comparison(co[i], co[j])
                mej[i, j] = v
                mej[j, i] = 1 - v
        return mej.sum(axis=1), mej

    def comparison(self, c1, c2):
        if not self.reverse:
            v1, v2 = self.expert_function(np.vstack([c1, c2]))
        else:
            v1, v2 = - self.expert_function(np.vstack([c1, c2]))

        if v1 == v2:
            return 0.5
        else:
            return v1 > v2

