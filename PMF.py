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
        self._p = multiplicands[0].p
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

    # change field size
    @property
    def p(self):
        return self._p

    @p.setter
    def p(self, x):
        for poly in self.multiplicands:
            poly.p = x
        self._p = x

    def __call__(self, *args, **kwargs):
        return self.eval(list(args))

    def __copy__(self):
        return PMF(self.multiplicands)

    def __mul__(self, other: MVLinear) -> 'PMF':
        return PMF(self.multiplicands + [other])

    __rmul__ = __mul__

    def __repr__(self):
        return f"Product[{','.join([poly.__repr__() for poly in self.multiplicands])}]"


class DummyPMF(PMF):
    def __init__(self, num_multiplicands: int, num_variables: int, p: int):
        super(DummyPMF, self).__init__([MVLinear(num_variables, dict(), p)])
        self._num_multiplicands = num_multiplicands
        self._num_variables = num_variables
        self._p = p

    def num_multiplicands(self) -> int:
        return self._num_multiplicands

    def eval(self, at: List[int]) -> int:
        raise NotImplementedError("Dummy PMF Evaluated. ")

    @property
    def p(self):
        return self._p

    def __call__(self, *args, **kwargs):
        raise NotImplementedError("Dummy PMF Evaluated. ")

    def __copy__(self):
        raise NotImplementedError("Dummy PMF Copied. ")

    def __mul__(self, other: MVLinear) -> 'PMF':
        raise NotImplementedError("Dummy PMF")

    def __repr__(self):
        return f"DummyPMF(num_multiplicands = {self._num_multiplicands}, " \
               f"num_variables = {self._num_variables}, p = {self._p})"
