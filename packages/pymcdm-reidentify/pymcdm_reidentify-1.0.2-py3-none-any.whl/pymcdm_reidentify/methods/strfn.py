# Copyright (c) 2024 Bartłomiej Kizielewicz

from .sfn import SFN

import numpy as np


def _TRFN(a, b, c, d):
    def trfn(x):
        res = np.zeros(x.shape)

        mask = np.logical_and(x >= a, x <= b)
        res[mask] = (x[mask] - a) / (b - a)

        mask = np.logical_and(x > b, x < c)
        res[mask] = 1

        mask = np.logical_and(x >= c, x <= d)
        res[mask] = (d - x[mask]) / (d - c)

        return np.clip(res, 0, 1)

    return trfn


class STRFN(SFN):
    """ Stochastic Trapezoidal Fuzzy Normalization (STRFN).

        STRFN is an approach based on fuzzy normalization using trapezoidal fuzzy numbers. This approach seeks the cores
        of trapezoidal fuzzy numbers used to normalize the decision matrix so that the MCDA/MCDM method combined with
        STRFN best reflects the reference ranking.

        Examples
        --------
        >>> import numpy as np
        >>> from mealpy.swarm_based.PSO import OriginalPSO
        >>> from pymcdm.methods import TOPSIS
        >>> from pymcdm_reidentify.methods import STRFN
        >>> matrix = np.random.random((1000, 2))
        >>> types = np.array([-1, 1])
        >>> weights = np.array([0.5, 0.5])
        >>> bounds = np.array([[0, 1], [0, 1]])
        >>> topsis = TOPSIS()
        >>> preference = topsis(matrix, weights, types)
        >>> rank = topsis.rank(preference)
        >>> stoch = OriginalPSO(epoch=1000, pop_size=100)
        >>> model = STRFN(stoch.solve, TOPSIS(), bounds)
        >>> model.fit(matrix, rank, log_to=None)
    """

    def __init__(self, method, base, fn_bounds, weights=None):
        """ Creates object of STRFN class.

        Parameters
        ----------
        method : callable
            A function used for optimization to find the best cores. It should include 'bounds', which denote the
            search boundaries for the cores; these boundaries are projected onto a FloatVar object from the MealPy
            library. The function should also include an argument to set 'obj_func', which is used according to the
            fuzzy normalization selection methodology. Additionally, it should have an argument to set 'minmax',
            which determines whether the function is minimized or maximized. It should also have an argument to set
            'n_dims', which indicates the number of criteria in the decision-making problem.

        base : object
            An object representing the MCDA/MCDM method for which the cores will be found. It should have a
            'normalization' attribute and be callable for evaluating alternatives (in this case, the training set).

        fn_bounds : list[list]
            Nested lists containing the boundary values for the trapezoidal fuzzy numbers used for normalization. These
            boundaries are used to declare the search bounds for the cores.

        weights : ndarray, optional
            Criteria weights. The sum of the weights should be 1 (e.g., sum(weights) == 1). If not provided, the weights
            are assigned equally in the 'fit' method.
        """
        super().__init__(method, base, weights)
        self.lb = [fuzzy_number[0] for fuzzy_number in fn_bounds for _ in range(2)]
        self.ub = [fuzzy_number[-1] for fuzzy_number in fn_bounds for _ in range(2)]

    def fit(self, x_train, y_train, **kwargs_method):
        super().fit(x_train, y_train, **kwargs_method)
        self.cores = [cores for pair in [[core1, core2] if core1 < core2 else [core2, core1]
                                         for core1, core2 in zip(self.cores[::2], self.cores[1::2])] for cores in pair]

    def get_fuzzy_numbers(self, cores):
        """ Method that returns a list of trapezoidal fuzzy numbers used for normalizing the decision matrix.

            Parameters
            ----------
            cores : ndarray
                Matrix representing the cores for trapezoidal fuzzy numbers.

            Returns
            -------
            list[callable]
                A list of trapezoidal fuzzy numbers represented as functions.
        """
        return [_TRFN(a, b, c, d) if b < c else _TRFN(a, c, b, d) for a, b, c, d in
                zip(self.lb[::2], cores[::2], cores[1::2], self.ub[1::2])]
