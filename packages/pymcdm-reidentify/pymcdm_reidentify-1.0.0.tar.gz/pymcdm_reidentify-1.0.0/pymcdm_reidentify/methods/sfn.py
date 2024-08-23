# Copyright (c) 2024 Bartłomiej Kizielewicz

from .stochastic_identification import StochasticIdentification
from abc import abstractmethod
from .. import normalizations
from pymcdm.correlations import rw
from mealpy import FloatVar
import numpy as np


class SFN(StochasticIdentification):
    """ Abstract class for Stochastic Fuzzy Normalization (SFN).

        SFN is an approach for the re-identification of MCDA/MCDM models using fuzzy numbers. The main concept involves
        finding values within the fuzzy numbers, known as cores, while keeping the boundary values of the fuzzy numbers
        constant.
    """

    def __init__(self, method, base, weights=None):
        """ Abstract initialization for SFN class.

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

        weights : ndarray, optional
            Criteria weights. The sum of the weights should be 1 (e.g., sum(weights) == 1). If not provided, the weights
            are assigned equally in the 'fit' method.
        """
        super().__init__(method)
        self.base = base
        self.lb = None
        self.ub = None
        self.cores = None
        self.weights = weights

    def __call__(self, *args, **kwargs):
        """ Method that returns a list of fuzzy numbers used for normalizing the decision matrix.

            Returns
            -------
            list[callable]
                A list of fuzzy numbers represented as functions.
        """
        return self.get_fuzzy_numbers(self.cores)

    def fit(self, x_train, y_train, **kwargs_method):
        """ Method for training to find the best core for fuzzy normalization that matches the given ranking.

            Parameters
            ----------
            x_train : ndarray
                Decision matrix used for training to find the best core for fuzzy normalization. Alternatives are in
                rows and criteria are in columns.

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
        self.cores = agent.solution

    def fitness(self, solutions, correlation=rw):
        """ Fitness method for finding the cores for fuzzy normalization.

            Parameters
            ----------
            solutions : ndarray
                Matrix representing the cores for fuzzy numbers.

            correlation : callable, optional
                A correlation coefficient function used to compare rankings during the search for the optimal cores.
                The default is `rw`.

            Returns
            -------
            float
                The correlation value between the reference ranking and the ranking obtained from the base method with
                fuzzy normalization based on the identified cores.
        """
        fuzzy_normalization = normalizations.FuzzyNormalization(self.get_fuzzy_numbers(solutions))
        types = np.ones(self.__x_train.shape[1])
        self.base.normalization = fuzzy_normalization
        preference = self.base(self.__x_train, self.weights, types)
        return correlation(self.base.rank(preference), self.__y_train)

    @abstractmethod
    def get_fuzzy_numbers(self, cores):
        """ Abstract method to be implemented in subclasses to convert cores to fuzzy numbers. """
        pass
