from unittest import TestCase
from test_GKRProver import randomGKR, randomPrime
from FSGKR import generateTheoremAndProof, verifyProof
import random


class Test(TestCase):
    def test_completeness(self):
        for _ in range(10):
            L = 6
            p = randomPrime(330)
            gkr = randomGKR(L, p)
            g = [random.randint(0, p-1) for _ in range(L)]
            thm, pf = generateTheoremAndProof(gkr, g)
            assert verifyProof(thm, pf)

