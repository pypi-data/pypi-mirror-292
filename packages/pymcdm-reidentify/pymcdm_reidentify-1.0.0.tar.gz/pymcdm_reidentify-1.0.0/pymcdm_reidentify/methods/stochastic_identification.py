# Copyright (c) 2024 Bartłomiej Kizielewicz

from abc import ABC, abstractmethod


class StochasticIdentification(ABC):
    """ Abstract class for stochastic re-identification methods.

        This class serves as a template for creating methods that utilize stochastic optimization to find the best
        solution for re-identification problems.
    """

    def __init__(self, method):
        """ Abstract initialization for StochasticIdentification class.

        Parameters
        ----------
        method : callable
            A function used for optimization to find the best solution.
        """
        self.method = method
        self.__y_train = None
        self.__x_train = None

    @abstractmethod
    def fit(self, x_train, y_train, **kwargs_method):
        """ Method for training to find the best solution.

            This method should be implemented in subclasses to perform the necessary training to identify the optimal
            solution using the provided decision matrix and rankings.

            Parameters
            ----------
            x_train : ndarray
                Decision matrix used for training. Alternatives are in rows and criteria are in columns.

            y_train : ndarray
                Ranking/preferences of the alternatives contained in 'x_train'.

            **kwargs_method : dict
                Dictionary of parameter settings for the optimization method 'self.method'.
        """
        pass

    @abstractmethod
    def fitness(self, solutions):
        """ Fitness method for evaluating the quality of a solution.

            This method should be implemented in subclasses to evaluate the fitness of potential solutions provided by
            the stochastic optimization method.

            Parameters
            ----------
            solutions : ndarray
                Possible solutions provided by the stochastic optimization method.
        """
        pass
