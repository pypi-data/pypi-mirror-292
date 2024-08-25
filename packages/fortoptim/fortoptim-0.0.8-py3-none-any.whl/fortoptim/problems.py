"""Module containing every test problem"""

import numpy as np

from fortoptim.problem import Problem


class Ackley(Problem):
    """
    https://en.wikipedia.org/wiki/Ackley_function
    https://pymoo.org/problems/single/ackley.html
    """

    def __init__(self, dim, a=20, b=1 / 5, c=2 * np.pi, **kwargs):
        super().__init__(dim=dim, **kwargs)

        self.a = a
        self.b = b
        self.c = c

    def get_gradients(self, x):
        a = self.a
        b = self.b
        c = self.c
        n = self.dim

        x_norm = np.linalg.norm(x, axis=1, keepdims=True)

        grads = -a * np.exp(-b / np.sqrt(n) * x_norm) * (
            -b / np.sqrt(n) * x / (x_norm + 1e-6)
        ) - np.exp(np.sum(np.cos(c * x), axis=1, keepdims=True) / n) * (
            c / n * np.sin(c * x)
        )
        return grads

    def get_values(self, x):
        a, b, c = self.a, self.b, self.c
        n = self.dim
        x_norm = np.linalg.norm(x, axis=1, keepdims=True)

        out = (
            -a * np.exp(-b / np.sqrt(n) * x_norm)
            - np.exp(np.sum(np.cos(x * c), axis=1, keepdims=True) / n)
            + a
            + np.exp(1)
        )
        return out

    def get_solution(self):
        return (np.zeros(shape=(1, self.dim)), 0.0)

    def is_solution(self, x):
        return np.isclose(self.get_values(x), 0.0)


class Booth(Problem):
    """
    f(x,y) = (x+2y-7)^2 + (2x + y -5)^2
    """

    def __init__(self, **kwargs):
        super().__init__(dim=2, **kwargs)

    def get_gradients(self, x):
        x1, x2 = x[:, 0], x[:, 1]
        grads_x = (x1 + 2 * x2 - 7) + (2 * x1 + x2 - 5) * 2
        grads_y = (x1 + 2 * x2 - 7) * 2 + (2 * x1 + x2 - 5)

        return np.stack([grads_x, grads_y], axis=1)

    def get_values(self, x):
        x1, x2 = x[:, 0:1], x[:, 1:2]
        values = (x1 + 2 * x2 - 7) ** 2 + (2 * x1 + x2 - 5) ** 2
        return values

    def get_solution(self):
        return (np.array([[1, 3]]), 0.0)

    def is_solution(self, x):
        return np.isclose(self.get_values(x), 0.0)


class Beale(Problem):
    """
    f(x, y) = (1.5 - x +xy)^2 + (2.25 - x + xy^2)^2 + (2.625 -x + xy^3)^2
    """

    def __init__(self, **kwargs):
        super().__init__(dim=2, **kwargs)

    def get_gradients(self, x):
        x1 = x[:, 0]
        x2 = x[:, 1]

        grads_x = (
            (1.5 - x1 + x1 * x2) * (-1 * x2)
            + (2.25 - x1 + x1 * x2**2) * (-1 * x2**2)
            + (2.625 - x1 + x1 * x2**3) * (-1 * x2**3)
        )

        grads_y = (
            (1.5 - x1 + x1 * x2) * x1
            + (2.25 - x1 + x1 * x2**2) * (2 * x1 * x2)
            + (2.625 - x1 + x1 * x2**3) * (3 * x1 * x2)
        )

        grads = np.stack([grads_x, grads_y], axis=1)
        return grads

    def get_values(self, x):
        x1 = x[:, 0:1]
        x2 = x[:, 1:2]
        out = (
            (1.5 - x1 + x1 * x2) ** 2
            + (2.25 - x1 + x1 * x2**2) ** 2
            + (2.625 - x1 + x1 * x2**3) ** 2
        )
        return out

    def get_solution(self):
        return (np.array([[3, 0.5]]), 0.0)

    def is_solution(self, x):
        return np.isclose(self.get_values(x), 0.0)


class Rosenbrock2D(Problem):
    """
    f(x1,x2) = (a-x1)**2 + b*(x2-x1**2)**2
    """

    def __init__(self, a=1, b=100, **kwargs):
        super().__init__(dim=2, **kwargs)
        self.a = a
        self.b = b

    def get_gradients(self, x):
        a, b = self.a, self.b

        x1 = x[:, 0]
        x2 = x[:, 1]

        grads_x = -2 * (a - x1) - 4 * x1 * b * (x2 - x1**2)
        grads_y = b * (x2 - x1**2)

        grads = np.stack([grads_x, grads_y], axis=1)

        return grads

    def get_values(self, x):
        x1 = x[:, 0:1]
        x2 = x[:, 1:2]
        return (self.a - x1) ** 2 + self.b * (x2 - x1**2) ** 2

    def get_solution(self):
        a = self.a
        return (np.array([[a, a**2]]), 0.0)

    def is_solution(self, x):
        return np.isclose(self.get_values(x), 0.0)


class Sphere(Problem):
    """
    f(X) = ||X||_2^2
    """

    def __init__(self, dim, **kwargs):
        super().__init__(dim=dim, **kwargs)

    def get_gradients(self, x):
        grads = 2 * x
        return grads

    def get_values(self, x):
        return np.sum(x, axis=1, keepdims=True)

    def get_solution(self):
        return (np.zeros(shape=(1, self.dim)), 0.0)

    def is_solution(self, x):
        return np.isclose(self.get_values(x), 0.0)
