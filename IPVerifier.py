from random import Random

from polynomial import MVLinear


class InteractiveVerifier:
    """
    An interactive verifier that verifies the sum of the multi-linear polynomial
    """

    def __init__(self, seed: int, polynomial: MVLinear, asserted_sum: int):
        """
        Initialize the protocol of the verifier.
        :param seed: the random source
        :param polynomial: The multilinear function
        :param asserted_sum: The proposed sum (0 and 1) of the multilinear function (which is to be verified)
        """
        self.p: int = polynomial.p
        self.poly: MVLinear = polynomial
        self.asserted_sum: int = asserted_sum % self.p
        self.rand: Random = Random()
        self.rand.seed(seed)

        self.active: bool = True
        self.convinced: bool = False

        # some edge case: if univariate or constant: no need to be interactive
        if polynomial.num_variables == 0:
            if (asserted_sum - polynomial.eval([])) % self.p == 0:
                self._convince_and_close()
                return
            else:
                self._reject_and_close()
                return
        if polynomial.num_variables == 1:
            result = (polynomial.eval([0]) + polynomial.eval([1])) % self.p
            if (asserted_sum - result) % self.p == 0:
                self._convince_and_close()
                return
            else:
                self._reject_and_close()
                return

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
