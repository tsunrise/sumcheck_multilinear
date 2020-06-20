import copy
from typing import Dict


class MVLinear:
    """
    A Sparse Representation of a multi-linear polynomial.
    """

    def __init__(self, num_variables: int, term: Dict[int, int], p: int):
        """
        :param num_variables: total number of variables
        :param term: the terms of the polynomial. Index is the binary representation of the vector, where
        the nth bit represents the nth variable. For example, 0b1011 represents term x0x1x3. The value represents the coefficient.
        :param p: the size of finite field
        """

        self.num_variables = num_variables
        self.terms: Dict[int, int] = dict()
        self.p = p
        for k in term:
            if k >> self.num_variables > 0:
                raise ValueError("Term is out of range.")
            if k in self.terms:
                self.terms[k] = (self.terms[k] + term[k]) % self.p
            else:
                self.terms[k] = term[k] % self.p

    def __repr__(self):
        s = ""
        s += "MVLinear("
        for k in self.terms:
            s += " + "
            s += str(self.terms[k])
            if k != 0:
                s += "*"

            i = 0
            while k != 0:
                if k & 1 == 1:
                    s += "x"+str(i)
                i += 1
                k >>= 1

        s += ")"
        return s

    def __copy__(self) -> 'MVLinear':
        t = self.terms.copy()
        return MVLinear(self.num_variables, t, self.p)
    __deepcopy__ = __copy__

    def __add__(self, other: 'MVLinear') -> 'MVLinear':
        if not isinstance(other, MVLinear):
            raise TypeError("MVLinear can only be added with MVLinear")
        if other.p != self.p:
            raise TypeError("The function being added is not in the same field. ")

        ans: MVLinear = copy.copy(self)
        ans.num_variables = max(self.num_variables, other.num_variables)

        for k in other.terms:
            if k in self.terms:
                ans.terms[k] = (ans.terms[k] + other.terms[k]) % self.p
                if ans.terms[k] == 0:
                    ans.terms.pop(k)
            else:
                ans.terms[k] = other.terms[k] % self.p

        return ans

    def __sub__(self, other):
        if not isinstance(other, MVLinear):
            raise TypeError("MVLinear can only be added with MVLinear")
        if other.p != self.p:
            raise TypeError("The function being added is not in the same field. ")

        ans: MVLinear = copy.copy(self)
        ans.num_variables = max(self.num_variables, other.num_variables)

        for k in other.terms:
            if k in self.terms:
                ans.terms[k] = (ans.terms[k] - other.terms[k]) % self.p
                if ans.terms[k] == 0:
                    ans.terms.pop(k)
            else:
                ans.terms[k] = other.terms[k] & self.p

        return ans
