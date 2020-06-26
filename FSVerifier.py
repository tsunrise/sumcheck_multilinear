import random
from typing import List, Tuple

from polynomial import MVLinear
import pickle
import hashlib
from IPVerifier import InteractiveVerifier


class Proof:
    """
    A data structure representing offline proof of multilinear sum.
    """

    def __init__(self, poly: MVLinear, assertedSum: int, proverMessage: List[Tuple[int, int]]):
        self.prover_message: List[Tuple[int, int]] = proverMessage
        self.poly: MVLinear = poly
        self.asserted_sum = assertedSum


def randomElement(poly: MVLinear, proverMessage: List[Tuple[int, int]], byteLength: int = 512):
    sha = hashlib.sha512()

    # append input: polynomial
    sha.update(pickle.dumps(poly))

    for msg_pair in proverMessage:
        p0 = msg_pair[0] % poly.p
        p1 = msg_pair[1] % poly.p

        sha.update(b'N')
        sha.update(p0.to_bytes(byteLength, 'little'))
        sha.update(b'X')
        sha.update(p1.to_bytes(byteLength, 'little'))

    result = int.from_bytes(sha.digest(), 'little') % poly.p
    return result


def verifyProof(proof: Proof, byteLength: int = 512) -> bool:
    v = PseudoRandomVerifier(random.randint(), proof.poly, proof.asserted_sum, byteLength)
    for msg_pair in proof.prover_message:
        result, _ = v.prove(msg_pair[0], msg_pair[1])
        if not result:
            return False

    return v.convinced


class PseudoRandomVerifier(InteractiveVerifier):
    def __init__(self, seed: int, polynomial: MVLinear, asserted_sum: int, byteLength: int = 512):
        super().__init__(seed, polynomial, asserted_sum)
        self.proverMessages: List[Tuple[int, int]] = []
        self.byteLength = byteLength

    def prove(self, p0: int, p1: int) -> Tuple[bool, int]:
        self.proverMessages.append((p0, p1))
        return super(PseudoRandomVerifier, self).prove(p0, p1)

    def randomR(self) -> int:
        return randomElement(self.poly, self.proverMessages, byteLength=self.byteLength)
