import copy
from typing import Dict, List, Union, Callable


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
                    s += "x" + str(i)
                i += 1
                k >>= 1

        s += ")"
        return s

    def __copy__(self) -> 'MVLinear':
        t = self.terms.copy()
        return MVLinear(self.num_variables, t, self.p)

    __deepcopy__ = __copy__

    def _assert_same_type(self, other: 'MVLinear'):
        if not isinstance(other, MVLinear):
            raise TypeError("MVLinear can only be added with MVLinear")
        if other.p != self.p:
            raise TypeError("The function being added is not in the same field. ")

    def __add__(self, other: Union['MVLinear', int]) -> 'MVLinear':
        if type(other) is int:
            other = MVLinear(self.num_variables, {0b0: other}, self.p)
        self._assert_same_type(other)

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

    __radd__ = __add__

    def __sub__(self, other: Union['MVLinear', int]) -> 'MVLinear':
        if type(other) is int:
            other = MVLinear(self.num_variables, {0b0: other}, self.p)
        self._assert_same_type(other)

        ans: MVLinear = copy.copy(self)
        ans.num_variables = max(self.num_variables, other.num_variables)

        for k in other.terms:
            if k in self.terms:
                ans.terms[k] = (ans.terms[k] - other.terms[k]) % self.p
                if ans.terms[k] == 0:
                    ans.terms.pop(k)
            else:
                ans.terms[k] = (- other.terms[k]) % self.p

        return ans

    def __rsub__(self, other):
        if type(other) is int:
            other = MVLinear(self.num_variables, {0b0: other}, self.p)
        return other - self

    def __mul__(self, other: Union['MVLinear', int]) -> 'MVLinear':
        if type(other) is int:
            other = MVLinear(self.num_variables, {0b0: other}, self.p)
        self._assert_same_type(other)

        terms: Dict[int, int] = dict()
        # naive n^2 poly multiplication where n is number of terms
        for sk in self.terms:  # the term of self
            for ok in other.terms:  # the term of others
                if sk & ok > 0:
                    raise ArithmeticError("The product is no longer multi-linear function.")
                nk = sk + ok  # the result term
                if nk in terms:
                    terms[nk] = (terms[nk] + self.terms[sk] * other.terms[ok]) % self.p
                else:
                    terms[nk] = (self.terms[sk] * other.terms[ok]) % self.p
                if terms[nk] == 0:
                    terms.pop(nk)

        ans = MVLinear(max(self.num_variables, other.num_variables), terms, self.p)
        return ans

    __rmul__ = __mul__  # commutative

    def eval(self, at: List[int]) -> int:
        s = 0
        for term in self.terms:
            i = 0
            val = self.terms[term]
            while term != 0:
                if term & 1 == 1:
                    val = (val * (at[i] % self.p)) % self.p
                if val == 0:
                    break
                term >>= 1
                i += 1
            s = (s + val) % self.p

        return s

    def __call__(self, *args, **kwargs) -> int:
        if len(args) == 0:
            return self.eval([])
        if isinstance(args[0], list):
            return self.eval(args[0])
        return self.eval(list(args))


def makeMVLinearConstructor(num_variables: int, p: int) -> Callable[[Dict[int, int]], MVLinear]:
    """
    Return a function that outputs MVLinear
    :param num_variables: total number of variables
    :param p: size of the field
    :return: Callable[[Dict[int, int]], MVLinear]
    """
    def f(term: Dict[int, int]) -> MVLinear:
        return MVLinear(num_variables, term, p)

    return f

