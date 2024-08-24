# Copyright (c) 2024 Bartłomiej Kizielewicz

import numpy as np
from pymcdm.correlations import rw
from .stochastic_identification import StochasticIdentification
from mealpy import FloatVar


class SITW(StochasticIdentification):
    """ Stochastic Identification of Weights (SITW) approach.

        The SITW approach involves finding the optimal weights for decision criteria in a given MCDA/MCDM method, so that
        the resulting rankings of alternatives are as close as possible to a reference ranking. Stochastic optimization
        methods are used to find these weights [#sitw]_.

        References
        ----------
        .. [#sitw] Kizielewicz, B., Paradowski, B., Więckowski, J., & Sałabun, W. (2022). Identification of weights in multi-cteria decision problems based on stochastic optimization.

        Examples
        --------
        >>> import numpy as np
        >>> from mealpy.swarm_based.PSO import OriginalPSO
        >>> from pymcdm.methods import TOPSIS
        >>> from pymcdm_reidentify.methods import SITW
        >>> # Exemplary data
        >>> matrix = np.random.random((1000, 2))
        >>> types = np.array([-1, 1])
        >>> weights = np.random.random((2))
        >>> weights = weights / np.sum(weights) # Unknown expert criteria weights
        >>> preference = TOPSIS()(matrix, weights, types)
        >>> rank = TOPSIS().rank(preference)
        >>> stoch = OriginalPSO(epoch=1000, pop_size=100)
        >>> model = SITW(stoch.solve, TOPSIS(), types)
        >>> model.fit(matrix, rank, log_to=None)
    """

    def __init__(self, method, base, types):
        """ Creates SITW object.

        Parameters
        ----------
        method : callable
            A function used for optimization to find the best weights for decision criteria. It should include
            'bounds', which denote the search boundaries for the weights; these boundaries are projected onto a
            FloatVar object from the MealPy library. The function should also include an argument to set 'obj_func',
            which is used according to the criteria weights selection methodology. Additionally, it should have an
            argument to set 'minmax', which determines whether the function is minimized or maximized. It should also
            have an argument to set 'n_dims', which indicates the number of criteria in the decision-making problem.

        base : object
            An object representing the MCDA/MCDM method for which the criteria weights will be found. This method should
            be able to process a weight vector where the sum of the weights is equal to 1.

        types : ndarray
            Array with definitions of criteria types:
            1 if a criterion is a profit criterion and -1 if a criterion is a cost criterion for each criterion in the
            decision matrix.
        """
        super().__init__(method)
        self.base = base
        self.types = types
        self.weights = None

        self.lb = np.zeros_like(self.types)
        self.ub = np.ones_like(self.types)

    def __call__(self, *args, **kwargs):
        """ Return the optimal weights found during the fitting process.

        Returns
        -------
        ndarray
            The weights for the decision criteria.
        """
        return self.weights


    def fit(self, x_train, y_train, **kwargs_method):
        """ Fit the model to find the optimal weights for the decision criteria.

        Parameters
        ----------
        x_train : ndarray
            Decision matrix used for training. Alternatives are in rows and criteria are in columns.

        y_train : ndarray
            Reference ranking of the alternatives.

        **kwargs_method : dict
            Dictionary of parameter settings for the optimization method 'self.method'.
        """
        self.__x_train = x_train
        self.__y_train = y_train

        kwargs_method['bounds'] = FloatVar(lb=self.lb, ub=self.ub)
        kwargs_method['obj_func'] = self.fitness
        kwargs_method['minmax'] = "max"
        kwargs_method['n_dims'] = len(self.lb)

        agent = self.method(kwargs_method)
        self.weights = agent.solution / np.sum(agent.solution)

    def fitness(self, solutions, correlation=rw):
        """Evaluate the fitness of a solution by comparing the ranking it produces with the reference ranking.

            Parameters
            ----------
            solutions : ndarray
                Array of unnormalized weights for the decision criteria. These weights are normalized within the
                fitness function.

            correlation : callable, optional
                A correlation coefficient function used to compare rankings. The default is `rw`.

            Returns
            -------
            float
                The correlation value between the ranking obtained using the MCDA method with the normalized weights
                and the reference ranking.
        """
        solutions = solutions / np.sum(solutions)
        preference = self.base(self.__x_train, solutions, self.types)
        return correlation(self.base.rank(preference), self.__y_train)
