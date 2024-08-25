"""Problem abstract class"""

from abc import ABC
from abc import abstractmethod


class Problem(ABC):
    """Problem abstract class"""

    def __init__(self, dim, constraints=None, multi_objective=False, **kargs):

        if constraints is not None and dim != len(constraints):
            raise ValueError('The number of constraints is different than the parameter space dimension.')

        self.multiple_objective = multi_objective
        self.dim = dim
        self.constraints = constraints

    #@abstractmethod
    def get_gradients(self, x):
        """return gradients at given points"""
        pass

    @abstractmethod
    def get_values(self, x):
        """return values at given points"""
        pass

    #@abstractmethod
    def get_solution(self):
        """return global minimum"""
        pass

    @abstractmethod
    def is_solution(self, x):
        """solution point and its value"""
        pass
