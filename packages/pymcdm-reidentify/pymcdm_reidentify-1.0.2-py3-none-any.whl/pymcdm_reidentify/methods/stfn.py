# Copyright (c) 2024 Bartłomiej Kizielewicz

from .sfn import SFN
from pymcdm.methods.comet import _TFN


class STFN(SFN):
    """ Stochastic Triangular Fuzzy Normalization (STFN).

        STFN is an approach based on fuzzy normalization using triangular fuzzy numbers. This approach seeks the cores
        of triangular fuzzy numbers used to normalize the decision matrix so that the MCDA/MCDM method combined with
        STFN best reflects the reference ranking [#stfn]_.

        References
        ----------
        .. [#stfn] Kizielewicz, B., & Dobryakova, L. (2023). Stochastic Triangular Fuzzy Number (S-TFN) Normalization: A New Approach for Nonmonotonic Normalization. Procedia Computer Science, 225, 4901-4911.


        Examples
        --------
        >>> import numpy as np
        >>> from mealpy.swarm_based.PSO import OriginalPSO
        >>> from pymcdm.methods import TOPSIS
        >>> from pymcdm_reidentify.methods import STFN
        >>> matrix = np.random.random((1000, 2))
        >>> types = np.array([-1, 1])
        >>> weights = np.array([0.5, 0.5])
        >>> bounds = np.array([[0, 1], [0, 1]])
        >>> topsis = TOPSIS()
        >>> preference = topsis(matrix, weights, types)
        >>> rank = topsis.rank(preference)
        >>> stoch = OriginalPSO(epoch=1000, pop_size=100)
        >>> model = STFN(stoch.solve, TOPSIS(), bounds)
        >>> model.fit(matrix, rank, log_to=None)
    """

    def __init__(self, method, base, fn_bounds, weights=None):
        """ Create object of STFN class.

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
            Nested lists containing the boundary values for the triangular fuzzy numbers used for normalization. These
            boundaries are used to declare the search bounds for the cores.

        weights : ndarray, optional
            Criteria weights. The sum of the weights should be 1 (e.g., sum(weights) == 1). If not provided, the weights
            are assigned equally in the 'fit' method.
        """
        super().__init__(method, base, weights)
        self.lb = [fuzzy_number[0] for fuzzy_number in fn_bounds]
        self.ub = [fuzzy_number[-1] for fuzzy_number in fn_bounds]

    def get_fuzzy_numbers(self, cores):
        """ Method that returns a list of triangular fuzzy numbers used for normalizing the decision matrix.

            Parameters
            ----------
            cores : ndarray
                Matrix representing the cores for triangular fuzzy numbers.

            Returns
            -------
            list[callable]
                A list of triangular fuzzy numbers represented as functions.
        """
        return [_TFN(a, m, b) for a, m, b in zip(self.lb, cores, self.ub)]
