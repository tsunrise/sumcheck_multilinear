from unittest import TestCase
from FSPMFVerifier import PMF, verifyProof
from FSPMFProver import generateTheoremAndProof
from polynomial import randomMVLinear


class Test(TestCase):
    def testCompleteness(self):
        for _ in range(100):
            p = PMF([randomMVLinear(6) for _ in range(10)])
            theorem, proof, _ = generateTheoremAndProof(p)
            self.assertTrue(verifyProof(theorem, proof))
