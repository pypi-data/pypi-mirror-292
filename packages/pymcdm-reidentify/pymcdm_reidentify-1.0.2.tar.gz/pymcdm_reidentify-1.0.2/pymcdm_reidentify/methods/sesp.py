# Copyright (c) 2024 Bartłomiej Kizielewicz

from .stochastic_identification import StochasticIdentification
from pymcdm.correlations import rw
from mealpy import FloatVar

import numpy as np


class SESP(StochasticIdentification):
    """ Stochastic Expected Solution Point (SESP) approach.

        SESP is an approach for the re-identification of MCDA/MCDM models based on a reference point called
        the Expected Solution Point. This approach was presented alongside the SPOTIS method in [#sesp]_.

        References
        ----------
        .. [#sesp] Kizielewicz, B., Więckowski, J., & Sałabun, W. (2024, June). SESP-SPOTIS: Advancing Stochastic Approach for Re-identifying MCDA Models. In International Conference on Computational Science (pp. 281-295). Cham: Springer Nature Switzerland.

        Examples
        --------
        >>> import numpy as np
        >>> from mealpy.swarm_based.PSO import OriginalPSO
        >>> from pymcdm.methods import SPOTIS
        >>> from pymcdm_reidentify.methods import SESP
        >>> matrix = np.random.random((1000, 2))
        >>> types = np.array([-1, 1])
        >>> weights = np.array([0.5, 0.5])
        >>> bounds = np.array([[0, 1],
        ...                    [0, 1]])
        >>> esp = np.array([0.5, 0.5]) # Unknown expert expected solution point
        >>> spotis = SPOTIS(bounds, esp)
        >>> preference = spotis(matrix, weights, types)
        >>> rank = spotis.rank(preference)
        >>> stoch = OriginalPSO(epoch=1000, pop_size=100)
        >>> model = SESP(stoch.solve, SPOTIS(bounds), types)
        >>> model.fit(matrix, rank, log_to=None)
    """

    def __init__(self, method, base, types, weights=None):
        """ Create SESP method object.

        Parameters
        ----------
        method : callable
            A function used for optimization to find the best ESP. It should include 'bounds', which denote the
            search boundaries for the point; these boundaries are projected onto a FloatVar object from the MealPy
            library. The function should also include an argument to set 'obj_func', which is used according to the
            ESP selection methodology. Additionally, it should have an argument to set 'minmax', which determines
            whether the function is minimized or maximized. It should also have an argument to set 'n_dims', which
            indicates the number of criteria in the decision-making problem.

        base : object
            An object representing the MCDA/MCDM method for which the ESP will be found. It should have an 'esp'
            attribute and be callable for evaluating alternatives (in this case, the training set). The callable should
            function similarly to the 'SPOTIS' method from the 'pymcdm' library.

        types : ndarray
            Array defining the criteria types: 1 if the criterion is profit and -1 if the criterion is cost for each
            criterion in the matrix.

        weights : ndarray, optional
            Criteria weights. The sum of the weights should be 1 (e.g., sum(weights) == 1). If not provided, the weights
            are assigned equally in 'fit' method.
        """
        super().__init__(method)
        self.types = types
        self.weights = weights
        self.base = base
        self.lb = self.base.bounds[:, 0]
        self.ub = self.base.bounds[:, 1]
        self.__bounds = None

    def __call__(self, *args, **kwargs):
        """ Method that returns the identified Expected Solution Point (ESP).

            Returns
            -------
            ndarray
                The identified ESP.
        """
        return self.esp

    def fit(self, x_train, y_train, **kwargs_method):
        """ Method for training to find the best Expected Solution Point (ESP) that matches the given ranking.

            Parameters
            ----------
            x_train : ndarray
                Decision matrix used for training (searching for) the best ESP. Alternatives are in rows and
                criteria are in columns.

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

        if self.weights is None:
            self.weights = np.ones(self.__x_train.shape[1]) / self.__x_train.shape[1]


        agent = self.method(kwargs_method)
        self.esp = agent.solution

    def fitness(self, solutions, correlation=rw):
        """ Fitness method for finding the Expected Solution Point (ESP).

            Parameters
            ----------
            solutions : ndarray
                Matrix representing the ESPs.

            correlation : callable, optional
                A correlation coefficient function used to compare rankings during the search for the optimal ESP.
                The default is `rw`.

            Returns
            -------
            float
                The correlation value between the reference ranking and the ranking obtained from the base method with
                the identified ESP.
        """
        self.base.esp = solutions
        preference = self.base(self.__x_train, self.weights, self.types)
        return correlation(self.base.rank(preference), self.__y_train)


