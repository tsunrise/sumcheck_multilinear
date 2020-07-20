from unittest import TestCase
from FSPMFVerifier import PMF, verifyProof
from FSPMFProver import generateTheoremAndProof
from polynomial import randomMVLinear, randomPrime


class Test(TestCase):
    def testCompleteness(self):
        for _ in range(100):
            P = randomPrime(224)
            p = PMF([randomMVLinear(7, prime=P) for _ in range(5)])
            theorem, proof, _ = generateTheoremAndProof(p)
            self.assertTrue(verifyProof(theorem, proof))
