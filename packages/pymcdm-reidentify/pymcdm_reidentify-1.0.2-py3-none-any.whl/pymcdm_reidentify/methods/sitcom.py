# Copyright (c) 2024 Bartłomiej Kizielewicz

import itertools
import numpy as np

from .stochastic_identification import StochasticIdentification
from pymcdm.methods import COMET
from pymcdm.correlations import rw
from mealpy import FloatVar


class SITCOM(StochasticIdentification):
    """ Stochastic IdenTification Of Models (SITCOM) approach.

        SITCOM is an approach based on determining the preferences of characteristic objects using the COMET method
        through stochastic optimization methods. The main advantage of this approach is the ability to re-identify the
        COMET model without re-engaging the decision-making expert [#sitcom1]_, [#sitcom2]_.

        References
        ----------
        .. [#sitcom1] Kizielewicz, B., & Sałabun, W. (2020). A new approach to identifying a multi-criteria decision model based on stochastic optimization techniques. Symmetry, 12(9), 1551.
        .. [#sitcom2] Kizielewicz, Bartłomiej. "Towards the identification of continuous decisional model: the accuracy testing in the SITCOM approach." Procedia Computer Science 207 (2022): 4390-4400.

        Examples
        --------
        >>> import numpy as np
        >>> from mealpy.swarm_based.PSO import OriginalPSO
        >>> from pymcdm.methods import COMET, TOPSIS
        >>> from pymcdm.methods.comet_tools import MethodExpert
        >>> from pymcdm_reidentify.methods import SITCOM
        >>> matrix = np.random.random((1000, 2))
        >>> types = np.array([-1, 1])
        >>> weights = np.array([0.5, 0.5])
        >>> cvalues = COMET.make_cvalues(matrix, 2)
        >>> comet = COMET(cvalues, MethodExpert(TOPSIS(), weights, types))
        >>> preference = comet(matrix)
        >>> rank = comet.rank(preference)
        >>> stoch = OriginalPSO(epoch=1000, pop_size=100)
        >>> model = SITCOM(stoch.solve, cvalues)
        >>> model.fit(matrix, rank, log_to=None)
    """

    def __init__(self, method, cvalues):
        """ Create SITCOM object.

        Parameters
        ----------
        method : callable
            A function used for optimization to find the best preferences of characteristic objects. It should include
            'bounds', which denote the search boundaries for the preferences; these boundaries are projected onto a
            FloatVar object from the MealPy library. The function should also include an argument to set 'obj_func',
            which is used according to the preferences of characteristics objects selection methodology. Additionally,
            it should have an argument to set 'minmax', which determines whether the function is minimized or maximized.
            It should also have an argument to set 'n_dims', which indicates the number of characteristic objects in
            the decision-making problem.

        cvalues : list[list]
            A list of characteristic values based on which characteristic objects are created for the SITCOM model. Each
            criterion should have at least two characteristic values, which should be provided in a nested list.
        """
        super().__init__(method)
        self.cvalues = cvalues

        con = len(list(itertools.product(*cvalues)))
        self.lb = [0] * con
        self.ub = [1] * con

        self.model = COMET(cvalues, lambda co: (np.arange(con), None))

    def __call__(self, *args, **kwargs):
        """ Method that returns the identified preferences of characteristics objects.

            Returns
            -------
            ndarray
                The preferences of characteristics objects.
        """
        return self.model.p

    def fit(self, x_train, y_train, **kwargs_method):
        """ Trains the model to find the best preferences for characteristic objects in the COMET model, matching
            the given ranking.

            Parameters
            ----------
            x_train : ndarray
                Decision matrix used for training to find the best preferences for characteristic objects. Alternatives
                are in rows and criteria are in columns.

            y_train : ndarray
                Ranking of the alternatives contained in 'x_train'.

            **kwargs_method
                Dictionary of parameter settings for the optimization method 'self.method'.
        """
        self.__x_train = x_train
        self.__y_train = y_train

        kwargs_method['bounds'] = FloatVar(lb=self.lb, ub=self.ub)
        kwargs_method['obj_func'] = self.fitness
        kwargs_method['minmax'] = "max"
        kwargs_method['n_dims'] = len(self.lb)

        agent = self.method(kwargs_method)
        self.model.p = agent.solution

    def fitness(self, solutions, correlation=rw):
        """ Fitness method for finding the preferences of characteristic objects in the COMET model.

            Parameters
            ----------
            solutions : ndarray
                Matrix representing the preferences of characteristic objects.

            correlation : callable, optional
                A correlation coefficient function used to compare rankings during the search for the optimal preferences
                of characteristic objects. The default is `rw`.

            Returns
            -------
            float
                The correlation value between the reference ranking and the ranking obtained from the COMET method with
                the identified preferences of characteristic objects.
        """
        sj = np.array(solutions)
        unique_values, indexes, counts = np.unique(sj, return_counts=True, return_inverse=True)

        k = len(unique_values)
        self.p = (np.arange(k) / (k - 1))[indexes]

        self.model.p = self.p
        preference = self.model(self.__x_train)
        rank = self.model.rank(preference)
        return correlation(self.__y_train, rank)
