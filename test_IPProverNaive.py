from typing import Dict
from unittest import TestCase
from IPProverNaive import InteractiveNaiveProver
from IPVerifier import InteractiveVerifier
from polynomial import makeMVLinearConstructor
import random
import time
class TestInteractiveNaiveProver(TestCase):
    """
    Assume verifier works
    """

    def testFunctionality(self):
        m = makeMVLinearConstructor(4, 47)
        x0 = m({1: 1})
        x1 = m({1 << 1: 1})
        x2 = m({1 << 2: 1})
        x3 = m({1 << 3: 1})

        p = random.randint(0, 46) * x0 + random.randint(0, 46) * x1 + random.randint(0, 46) * x2 + \
            random.randint(0, 46) * x3
        print("Testing Polynomial: " + str(p))

        pv = InteractiveNaiveProver(p)
        s = pv.calculateSum([])
        print("Asserted sum: {}".format(s))

        v = InteractiveVerifier(random.randint(0, 0xFFFFFFFF), p, s)
        result, vT = pv.attemptProve(v)
        self.assertTrue(result, "Fail to prove the sum. ")
        self.assertTrue(v.convinced, "Verifier not convinced. ")

    def testBenchMark(self):
        num_variables = 12
        num_terms = 1500
        m = makeMVLinearConstructor(num_variables, 199)

        d: Dict[int, int] = dict()
        for _ in range(num_terms):
            d[random.randint(0, 2**num_variables - 1)] = random.randint(0, 198)

        p = m(d)
        pv = InteractiveNaiveProver(p)
        asum = pv.calculateSum([])
        v = InteractiveVerifier(random.randint(0, 0xFFFFFFFF), p, asum)

        t0 = time.time() * 1000
        _, vT = pv.attemptProve(v)
        t1 = time.time() * 1000

        self.assertTrue(v.convinced, "Verifier is not convinced.")
        print("Prover takes {0}ms, verifier takes {1}ms".format(t1 - t0 - vT, vT))
