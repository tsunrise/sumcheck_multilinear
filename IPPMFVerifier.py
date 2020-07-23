import math
from random import Random
from typing import List, Tuple

from PMF import PMF

MAX_ALLOWED_SOUNDNESS_ERROR = 2e-64


class InteractivePMFVerifier:
    """
    An interactive verifier that verifies the sum of the polynomial which is the product of multilinear functions
    """

    def __init__(self, seed: int, poly: PMF, asserted_sum: int,
                 maxAllowedSoundnessError: float = MAX_ALLOWED_SOUNDNESS_ERROR, checksum_only: bool = False):
        self.checksum_only: bool = checksum_only

        self.p = poly.p
        self.poly = poly
        self.asserted_sum = asserted_sum % self.p
        self.rand: Random = Random()
        self.rand.seed(seed)

        self.active: bool = True
        self.convinced: bool = False

        # check soundness
        if self.soundnessError() > maxAllowedSoundnessError:
            raise SoundnessErrorException(f"Soundness error {self.soundnessError()} exceeds maximum "
                                          f"allowed soundness error {maxAllowedSoundnessError}\n"
                                          f"Try to have a prime "
                                          f"with size "
                                          f">= {self.requiredFieldLengthBit(maxAllowedSoundnessError)} bits")


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

    def soundnessError(self) -> float:
        poly = self.poly
        deg = poly.num_variables * poly.num_multiplicands()

        return (self.poly.num_variables * deg) / self.p

    def requiredFieldLengthBit(self, e: float) -> int:
        """
        :param e: the maximum allowed soundness error
        :return: The minimum size of prime required to meet the soundness error constraint.
        """
        poly = self.poly
        deg = poly.num_variables * poly.num_multiplicands()
        minP = (self.poly.num_variables * deg) / e
        return math.ceil(math.log(minP, 2))

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
        if self.checksum_only:
            """
            When checksum_only is on, the verifier do not access the polynomial. It only 
            verifies that the sum of a polynomial is correct. 
            User often use this verifier as a subroutine, and uses self.subclaim() to get a sub-claim for
            the polynomial. 
            """
            self._convince_and_close()
            return True, 0
        final_sum = self.poly.eval(self.points)
        if pr != final_sum:
            self._reject_and_close()
            return False, 0
        self._convince_and_close()
        return True, 0

    def sub_claim(self) -> Tuple[List[int], int]:
        """
        The verifier should already checks the sum of the polynomial. If the sum is indeed the sum of polynomial, then
        the sub claim should be correct.
        The sub claim is in the following form:
        - one point of the polynomial
        - the expected evaluation at this point
        :return: Tuple[point: List[int], expected: int]
        """
        if not self.convinced:
            raise ArithmeticError("The verifier is not convinced, and cannot make a sub claim.")
        return self.points, self.expect

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

    def _repr_html_(self):
        if self.active:
            status = f"🕒 Active ({self.round}/{self.poly.num_variables})"
            style = "background-color: aqua; color:black; border-radius: 5px"
        elif self.convinced:
            status = f"✔ Convinced"
            style = "background-color: green; color:white; border-radius: 5px"
        else:
            status = f"❌ Reject"
            style = "background-color: red; color:white; border-radius: 5px"

        return f"<a style='{style}'>{status}</a> <b>PMFVerifier</b>(<i>#Multiplicands</i>={self.poly.num_multiplicands()}," \
               f" <i>#Variables</i>={self.poly.num_variables}, <i>P</i>={self.p})"

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

class SoundnessErrorException(Exception):
    pass