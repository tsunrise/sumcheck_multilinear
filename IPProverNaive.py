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
        lst[i] = b & 1
        b >>= 1
        i += 1
    return lst

class InteractiveNaiveProver:
    """
    A naive honest prover of sum-check protocol for multilinear polynomial.
    """

    def __init__(self, polynomial: MVLinear):
        self.poly: MVLinear = polynomial
        self.p = self.poly.p  # field size

    def attemptProve(self, verifier: InteractiveVerifier) -> Tuple[bool, float]:
        """
        Attempt to prove the sum.
        :param verifier:
        :return: Whether the verifier accepts the proof; the running time of verifier
        """
        fixed: List[int] = []
        vTime: float = 0
        while verifier.active:
            p0 = self.calculateSum(fixed + [0])
            p1 = self.calculateSum(fixed + [1])
            start = time.time() * 1000
            accept, r = verifier.prove(p0, p1)
            end = time.time() * 1000
            vTime += (end - start)
            if not accept:
                return False, vTime
            fixed.append(r)

        return verifier.convinced, vTime

    def calculateSum(self, fixed: List[int]) -> int:
        """
        Calculate the sum. The previous len(fixed) argument of the polynomial is fixed.
        :param fixed:
        :return: the sum
        """
        s = 0
        for p in range(2 ** (self.poly.num_variables - len(fixed))):
            result = self.poly.eval(fixed + binaryToList(p, self.poly.num_variables))
            s = (s + result) % self.p

        return s

