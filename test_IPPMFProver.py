import random
from unittest import TestCase
from IPPMFProver import InteractivePMFProver, InteractivePMFVerifier
from PMF import PMF
from polynomial import randomMVLinear


class TestInteractivePMFProver(TestCase):
    def testCompleteness(self):
        for _ in range(100):
            p = PMF([randomMVLinear(7) for _ in range(5)])
            pv = InteractivePMFProver(p)
            As, s = pv.calculateAllBookKeepingTables()
            v = InteractivePMFVerifier(random.randint(0, 0xFFFFFFFFFFFFFFFF), p, s)
            pv.attemptProve(As, v)

            self.assertTrue(v.convinced)


