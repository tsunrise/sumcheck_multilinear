from copy import copy
from typing import List

from PMF import PMF
from polynomial import MVLinear


class GKR:
    def __init__(self, f1: MVLinear, f2: MVLinear, f3: MVLinear):
        if not (f1.p == f2.p and f2.p == f3.p):
            raise ArithmeticError("Field Size Mismatch")

        if not (f1.num_variables != 3 * f2.num_variables) and (f1.num_variables != 3 * f3.num_variables):
            raise ArithmeticError("Expect: (f1.num_variables != 3 * f2.num_variables) "
                                  "and (f1.num_variables != 3 * f3.num_variables)")

        self.f1 = f1
        self.f2 = f2
        self.f3 = f3

        self.L = f2.num_variables  #  means "l" in paper

    def to_naive_product(self, g: List[int]) -> PMF:
        """
        Fix g and convert the GKR to the product of three multilinear function of 2l variables.
        :param g: first l variables of f1 (being fixed)
        :return PMF
        """

        f1 = self.f1.eval_part(g)

        f2 = copy(self.f2)
        f2.num_variables *= 2

        f3 = copy(self.f3)
        f3.num_variables *= 2
        old_keys = list(f3.terms.keys())
        for k in old_keys:
            f3.terms[k << self.L] = f3.terms.pop(k)

        return PMF([f1, f2, f3])

