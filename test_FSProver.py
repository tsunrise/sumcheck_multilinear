from unittest import TestCase
from FSVerifier import verifyProof
from FSProver import generateTheoremAndProof
from polynomial import randomMVLinear


class Test(TestCase):
    def testCompleteness(self):
        for i in range(100):
            p = randomMVLinear(7)
            theorem, proof = generateTheoremAndProof(p)
            assert verifyProof(theorem, proof)
