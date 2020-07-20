from typing import List, Tuple

from IPPMFVerifier import InteractivePMFVerifier
from PMF import PMF

def binaryToList(b: int, numVariables: int) -> List[int]:
    """
    Change binary form to list of arguments.
    :param b: The binary form. For example: 0b1011 means g(x0=1, x1 = 0, x2 = 1, x3 = 1)
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


class InteractivePMFProver:
    """
    A linear honest prover of sum-check protocol for product of multilinear polynomials using dynamic programming.
    """

    def __init__(self, polynomial: PMF):
        self.poly: PMF = polynomial
        self.p = self.poly.p  # field size

    def attemptProve(self, As: List[List[int]], verifier: InteractivePMFVerifier) -> None:
        """
        Attempt to prove the sum.
        :param As: The bookkeeping table for each MVLinear in the PMF
        :param verifier: the active interactive PMF verifier instance
        :return: the running time of verifier
        """
        l = self.poly.num_variables
        # vT: float = 0
        for i in range(1, l + 1):  # round
            products_sum: List[int] = [0] * (self.poly.num_multiplicands() + 1)
            for b in range(2 ** (l - i)):  # assignment
                for t in range(self.poly.num_multiplicands() + 1):  # point evaluation
                    product = 1
                    for j in range(self.poly.num_multiplicands()):  # iterate over multiplicands to multiply
                        A = As[j]
                        product = product * (
                                ((A[b << 1] * ((1 - t) % self.p)) + (A[(b << 1) + 1] * t) % self.p) % self.p) % self.p
                    products_sum[t] = (products_sum[t] + product) % self.p

            result, r = verifier.talk(products_sum)

            assert result
            for j in range(self.poly.num_multiplicands()):
                for b in range(2**(l-i)):
                    As[j][b] = (As[j][b << 1] * (1 - r) + As[j][(b << 1) + 1] * r) % self.p



    def calculateSingleTable(self, index: int) -> List[int]:
        """
        Calculate the bookkeeping table of a single MVLinear in the PMF.

        :param index: the index of the MVLinear in PMF
        :return: A bookkeeping table where the index is the binary form of argument of polynomial and value is the
        evaluated value
        """

        if index >= self.poly.num_multiplicands():
            raise IndexError(f"PMF has only {self.poly.num_multiplicands()} multiplicands. index = {index}")

        A: List[int] = [0] * (2 ** self.poly.num_variables)
        for p in range(2 ** self.poly.num_variables):
            A[p] = self.poly.multiplicands[index].eval(binaryToList(p, self.poly.num_variables))

        return A

    def calculateAllBookKeepingTables(self) -> Tuple[List[List[int]], int]:
        """
        For all multiplicands of the PMF, calculate its bookkeeping table.The function all calculates the sum.
        :return: All bookkeeping table. The sum of the PMF.
        """

        S: List[int] = [1] * (2 ** self.poly.num_variables)
        As: List[List[int]] = []
        for i in range(self.poly.num_multiplicands()):
            A = self.calculateSingleTable(i)
            # todo: might use vectorization here
            for j in range(2 ** self.poly.num_variables):
                S[j] = (S[j] * A[j]) % self.p

            As.append(A)

        s = 0
        for x in S:
            s = (s + x) % self.p

        return As, s


