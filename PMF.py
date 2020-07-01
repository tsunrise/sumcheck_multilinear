from copy import copy
from typing import List

from polynomial import MVLinear


class PMF:
    """
    Product of multilinear functions.
    """

    def __init__(self, multiplicands: List[MVLinear]):
        if len(multiplicands) == 0:
            raise ValueError("Multiplicands are empty.")
        self.num_variables = multiplicands[0].num_variables
        self.p = multiplicands[0].p
        for poly in multiplicands:
            self.num_variables = max(self.num_variables, poly.num_variables)
            if poly.p != self.p:
                raise ValueError("Field size mismatch.")

        self.multiplicands: List[MVLinear] = [copy(poly) for poly in multiplicands]

    def num_multiplicands(self) -> int:
        return len(self.multiplicands)

    def eval(self, at: List[int]) -> int:
        result = 1
        for poly in self.multiplicands:
            result = (result * poly.eval(at)) % self.p

        return result

    def __call__(self, *args, **kwargs):
        return self.eval(list(args))

    def __copy__(self):
        return PMF(self.multiplicands)

    def __mul__(self, other: MVLinear) -> 'PMF':
        return PMF(self.multiplicands + [other])

    __rmul__ = __mul__

    def __repr__(self):
        return f"Product[{','.join([poly.__repr__() for poly in self.multiplicands])}]"
