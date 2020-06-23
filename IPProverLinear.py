from typing import List, Tuple

from polynomial import MVLinear
from IPVerifier import InteractiveVerifier
import time


def binaryToList(b: int, numVariables: int) -> List[int]:
    """
    Change binary form to list of arguments.
    :param b: The binary form. For example: 0b1011 means g(x0=1, x1 = 1, x2 = 0, x3 = 1)
    :param numVariables: The number of variables
    :return:
    """
    lst: List[int] = [0] * numVariables
    i = 0
    while b != 0:
        lst[numVariables - i - 1] = b & 1
        b >>= 1
        i += 1
    return lst


class InteractiveLinearProver:
    """
    A linear honest prover of sum-check protocol for multilinear polynomial using dynamic programming.
    """

    def __init__(self, polynomial: MVLinear):
        self.poly: MVLinear = polynomial
        self.p = self.poly.p  # field size

    def attemptProve(self, A, verifier: InteractiveVerifier) -> None:
        """
        Attempt to prove the sum.
        :param verifier:
        :return: Whether the verifier accepts the proof; the running time of verifier
        """
        l = self.poly.num_variables
        for i in range(1, l + 1):  # round
            p0 = 0  # sum over P(fixed, 0, ...)
            p1 = 0  # sum over P(fixed, 1, ...)
            for b in range(2**(l-i)):
                p0 += A[b]
                p1 += A[b + 2**(l-i)]

            result, r = verifier.prove(p0, p1)

            for b in range(2**(l-i)):
                A[b] = (A[b] * (1 - r) + A[b + 2**(l - i)] * r) % self.p


    def calculateTable(self) -> Tuple[List[int], int]:
        """
        :return: A bookkeeping table where the index is the binary form of argument of polynomial and value is the
        evaluated value; the sum
        """

        A: List[int] = [0] * (2 ** self.poly.num_variables)
        s = 0
        for p in range(2 ** self.poly.num_variables):
            A[p] = self.poly.eval(binaryToList(p, self.poly.num_variables))
            s = (s + A[p]) % self.p

        return A, s
