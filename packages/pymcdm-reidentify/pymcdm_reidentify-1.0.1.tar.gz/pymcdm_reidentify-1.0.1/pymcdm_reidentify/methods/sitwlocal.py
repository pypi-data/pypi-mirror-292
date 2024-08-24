# Copyright (c) 2024 Bartłomiej Kizielewicz

import numpy as np
from .stochastic_identification import StochasticIdentification
from pymcdm.methods.comet_tools import MethodExpert, get_local_weights
from pymcdm.methods import COMET
from mealpy import FloatVar


class SITWLocal(StochasticIdentification):
    """ Stochastic Identification of Weights based Local weights (SITWLocal) approach.

        The SITWLocal approach is designed to identify weights for an MCDA/MCDM model that evaluates characteristic
        objects using the COMET method. This approach determines local weights for selected alternatives from the COMET
        approach by finding weights for the MCDA/MCDM model that minimize the mean absolute error (MAE) between the
        local weights derived from the model and the reference local weights [#sitwlocal]_.

        References
        ----------
        .. [#sitwlocal] Kizielewicz, B., Wiȩckowski, J., Paradowski, B., Shekhovtsov, A., Wątróbski, J., & Sałabun, W. (2024, April). Stochastic Approaches for Criteria Weight Identification in Multi-criteria Decision Analysis. In Asian Conference on Intelligent Information and Database Systems (pp. 40-51). Singapore: Springer Nature Singapore.


        Examples
        --------
        >>> import numpy as np
        >>> from mealpy.swarm_based.PSO import OriginalPSO
        >>> from pymcdm.methods import COMET, TOPSIS
        >>> from pymcdm.methods.comet_tools import MethodExpert, get_local_weights
        >>> from pymcdm_reidentify.methods import SITWLocal
        >>> matrix = np.random.random((1000, 2))
        >>> types = np.array([-1, 1])
        >>> weights = np.array([0.5, 0.5])
        >>> model = COMET(COMET.make_cvalues(matrix, 3), MethodExpert(TOPSIS(), weights, types))
        >>> y_train = np.array([get_local_weights(model, alt, percent_step=0.01) for alt in matrix])
        >>> stoch = OriginalPSO(epoch=1000, pop_size=100)
        >>> model = SITWLocal(stoch.solve, TOPSIS(), types)
        >>> model.fit(matrix, y_train)
    """

    def __init__(self, method, base, types):
        """ Creates object of the SITWLocal class.

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
                Preference of the alternatives. Preference values for alternatives must be in the range [0, 1].

            **kwargs_method : dict
                Dictionary of parameter settings for the optimization method 'self.method'.
        """
        self.__x_train = x_train
        self.__y_train = y_train

        kwargs_method['bounds'] = FloatVar(lb=self.lb, ub=self.ub)
        kwargs_method['obj_func'] = self.fitness
        kwargs_method['minmax'] = "min"
        kwargs_method['n_dims'] = len(self.lb)

        agent = self.method(kwargs_method)
        self.weights = agent.solution / np.sum(agent.solution)

    def fitness(self, solutions):
        """ Evaluate the fitness of a solution by comparing the preference it produces with the reference preference.

            Parameters
            ----------
            solutions : ndarray
                Array of unnormalized weights for the decision criteria. These weights are normalized within the
                fitness function.

            Returns
            -------
            float
                The mean absolute error (MAE) value between the preference obtained using the Expert MCDA method with
                the normalized weights in the COMET method and the reference preference.
        """
        solutions = solutions / np.sum(solutions)
        model = COMET(COMET.make_cvalues(self.__x_train, 3),
                      MethodExpert(self.base, solutions, self.types))
        y_pred = np.array([get_local_weights(model, alt, percent_step=0.01) for alt in self.__x_train])
        return np.mean(np.abs(y_pred - self.__y_train))
