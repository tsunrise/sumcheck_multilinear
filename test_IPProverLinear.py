import random
from typing import Dict
from unittest import TestCase
import time
from IPProverLinear import InteractiveLinearProver
from IPVerifier import InteractiveVerifier
from polynomial import makeMVLinearConstructor, randomPrime


class TestInteractiveLinearProver(TestCase):
    def testFunctionality(self):
        P = randomPrime(37)
        m = makeMVLinearConstructor(4, P)
        x0 = m({1: 1})
        x1 = m({1 << 1: 1})
        x2 = m({1 << 2: 1})
        x3 = m({1 << 3: 1})

        p = random.randint(0, P-1) * x0 + random.randint(0, P-1) * x1 + random.randint(0, P-1) * x2 + \
            random.randint(0, P-1) * x3
        print("Testing Polynomial: " + str(p))

        pv = InteractiveLinearProver(p)
        A, s = pv.calculateTable()
        print("Asserted sum: {}".format(s))

        v = InteractiveVerifier(random.randint(0, 0xFFFFFFFF), p, s)
        pv.attemptProve(A, v, showDialog=True)
        self.assertTrue(v.convinced, "Verifier not convinced. ")

    def testBenchMark(self):
        num_variables = 12
        num_terms = 2**11
        P = randomPrime(41)
        m = makeMVLinearConstructor(num_variables, P)

        d: Dict[int, int] = dict()
        for _ in range(num_terms):
            d[random.randint(0, 2**num_variables - 1)] = random.randint(0, P-1)

        p = m(d)
        pv = InteractiveLinearProver(p)
        t0 = time.time() * 1000
        A, asum = pv.calculateTable()
        t1 = time.time() * 1000
        t = t1 - t0
        v = InteractiveVerifier(random.randint(0, 0xFFFFFFFF), p, asum)
        t0 = time.time() * 1000
        vT = pv.attemptProve(A, v)
        t1 = time.time() * 1000
        t += t1 - t0

        self.assertTrue(v.convinced, "Verifier is not convinced.")
        print("Prover takes {0}ms, verifier takes {1}ms".format(t - vT, vT))