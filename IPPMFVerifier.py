from random import Random
from typing import List, Tuple

from IPVerifier import InteractiveVerifier
from PMF import PMF


class InteractivePMFVerifier:
    """
    An interactive verifier that verifies the sum of the polynomial which is the product of multilinear functions
    """

    def __init__(self, seed: int, poly: PMF, asserted_sum: int):
        self.p = poly.p

        self.poly = poly
        self.asserted_sum = asserted_sum % self.p
        self.rand: Random = Random()
        self.rand.seed(seed)

        self.active: bool = True
        self.convinced: bool = False

        # some edge case: if univariate or constant: no need to be interactive
        if poly.num_variables == 0:
            if (asserted_sum - poly.eval([])) % self.p == 0:
                self._convince_and_close()
                return
            else:
                self._reject_and_close()
                return
        if poly.num_variables == 1:
            result = (poly.eval([0]) + poly.eval([1])) % self.p
            if (asserted_sum - result) % self.p == 0:
                self._convince_and_close()
                return
            else:
                self._reject_and_close()
                return

        self.points: List[int] = [0] * self.poly.num_variables
        """
        the fixed points that are already decided by the verifier. At round i, [0, i-1] are decided
        """

        self.round: int = 0
        """
        which variable the verifier is summing (at round i, var 0 to var (i-1) is fixed, and the verifier is listening 
        to the univariate function of variable i where var[i+1, n] is summed over.  
        """

        self.expect: int = self.asserted_sum
        """
        The expected sum value at round i
        """

    def randomR(self) -> int:
        return self.rand.randint(0, self.p)

    def talk(self, msgs: List[int]) -> Tuple[bool, int]:
        """
        Send this verifier the univariate polynomial P(x). P(x) has degree at most the number of multiplicands.
        :param msgs: [P(0), P(1), ..., P(m)] where m is the number of multiplicands
        :return: accepted, r
        """

        if not self.active:
            raise RuntimeError("Unable to prove: the protocol is not active")

        if len(msgs) != (self.poly.num_multiplicands() + 1):
            raise ValueError(f"Malformed message: Expect {self.poly.num_multiplicands() + 1} points, but got "
                             f"{len(msgs)}")

        p0 = msgs[0] % self.p
        p1 = msgs[1] % self.p
        if (p0 + p1) % self.p != self.expect % self.p:
            self._reject_and_close()
            return False, 0

        # pick r at random
        r: int = self.randomR()
        pr: int = interpolate(msgs, r, self.p)

        self.expect = pr
        self.points[self.round] = r

        # if not final step, end here
        if not (self.round + 1 == self.poly.num_variables):
            self.round += 1
            return True, r

        # final step: check all
        final_sum = self.poly.eval(self.points)
        if pr != final_sum:
            self._reject_and_close()
            return False, 0
        self._convince_and_close()
        return True, 0

    def _convince_and_close(self):
        """
        Accept the sum. Close the protocol.
        """
        self.convinced = True
        self.active = False

    def _reject_and_close(self):
        """
        Reject the sum. Close the protocol
        """
        self.convinced = False
        self.active = False


def modInverse(a: int, m: int):
    """
    modular inverse (https://www.geeksforgeeks.org/multiplicative-inverse-under-modulo-m/)
    :param a: a
    :param m: prime
    :return: a^-1 mod p
    """

    m0 = m
    y = 0
    x = 1

    if m == 1:
        return 0

    while a > 1:
        q = a // m
        t = m
        m = a % m
        a = t
        t = y
        y = x - q * y
        x = t
    if x < 0:
        x += m0
    return x


def interpolate(points: List[int], r: int, p: int):
    """
    Interpolate and evaluate a PMF.
    Adapted from https://www.geeksforgeeks.org/lagranges-interpolation/
    :param points: P_0, P_1, P_2, ..., P_m where P is the product of m multilinear polynomials
    :param r: The point we want to evaluate at. In this scenario, the verifier wants to evaluate p_r.
    :param p: Field size.
    :return: P_r
    """

    result = 0
    for i in range(len(points)):

        term = points[i] % p
        for j in range(len(points)):
            if j != i:
                term = (term * ((r - j) % p) * modInverse((i - j) % p, p)) % p

        result = (result + term) % p

    return result
