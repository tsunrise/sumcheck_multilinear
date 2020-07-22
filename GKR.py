from copy import copy
from typing import List, Dict

from PMF import PMF


class GKR:
    def __init__(self, f1: Dict[int, int], f2: List[int], f3: List[int], p: int, L: int):
        """
        :param f1: Sparse polynomial f1(g,x,y) represented by a map of argument and its evaluation. Argument is little
        endian binary form. For example, 0b10111 means f(1,1,1,0,1)
        :param f2: Dense polynomial represented by a map of argument (index) and its evaluation (value).
        :param f3: Dense polynomial represented by a map of argument (index) and its evaluation (value).
        :param p: field size
        :param L: number of variables in f2 and f3
        """
        assert len(f2) == (1 << L), "f2(x) should have size 2^L"
        assert len(f3) == (1 << L), "f3(y) should have size 2^L"

        for k in f1.keys():
            if k >= (1 << (3*L)):
                raise ArithmeticError(f"f1 has invalid term {bin(k)} cannot be represented by {3*L} variables. ")

        self.f1 = f1.copy()
        self.f2 = f2.copy()
        self.f3 = f3.copy()

        self.L = L   # means "l" in paper
        self.p = p


