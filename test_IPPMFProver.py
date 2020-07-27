import random
from unittest import TestCase
from IPPMFProver import InteractivePMFProver, InteractivePMFVerifier
from PMF import PMF
from polynomial import randomMVLinear, randomPrime


class TestInteractivePMFProver(TestCase):
    def testCompleteness(self):
        for _ in range(100):
            P = randomPrime(221)
            p = PMF([randomMVLinear(7, prime=P) for _ in range(5)])
            pv = InteractivePMFProver(p)
            As, s = pv.calculateAllBookKeepingTables()
            v = InteractivePMFVerifier(p, s)
            pv.attemptProve(As, v)

            self.assertTrue(v.convinced)


